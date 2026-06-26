import json
from core.a2a_protocol import A2AMessage
from tools.tools import (
    sentiment_scorer, 
    topic_tagger, 
    theme_clusterer, 
    impact_scorer, 
    roadmap_deduplicator
)

def _load_taxonomy() -> list[str]:
    try:
        with open("memory/long_term_store.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("product_taxonomy", [])
    except Exception:
        return []

def _load_past_roadmap() -> list[str]:
    try:
        with open("memory/long_term_store.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("past_roadmap", [])
    except Exception:
        return []

def tagger_worker(task: A2AMessage) -> A2AMessage:
    """
    Tags items with sentiment and topic.
    Returns A2AMessage with structured JSON.
    """
    items = task.payload.get("items", [])
    taxonomy = _load_taxonomy()
    tagged_items = []
    
    for item in items:
        text = item.get("text", "")
        sentiment_res = sentiment_scorer(text)
        topic_res = topic_tagger(text, taxonomy)
        
        # severity is 1-5, we derive it from sentiment (negative = higher severity)
        if sentiment_res["sentiment"] == "negative":
            severity = 4.0 + sentiment_res["confidence"]
        elif sentiment_res["sentiment"] == "positive":
            severity = 1.0 + (1 - sentiment_res["confidence"])
        else:
            severity = 2.5
            
        tagged_items.append({
            "id": item.get("id"),
            "text": text,
            "sentiment": sentiment_res["sentiment"],
            "topic": topic_res["topic"],
            "severity": min(5.0, max(1.0, severity))
        })
        
    task.payload["items"] = tagged_items
    task.status = "DONE"
    return task

def cluster_worker(task: A2AMessage) -> A2AMessage:
    """
    Groups tagged items into themes.
    """
    items = task.payload.get("items", [])
    clusters = theme_clusterer(items)
    
    task.payload["clusters"] = clusters
    task.status = "DONE"
    return task

def ranker_worker(task: A2AMessage) -> A2AMessage:
    """
    Scores clusters based on frequency, severity, recency.
    """
    clusters = task.payload.get("clusters", [])
    max_count = max([c.get("item_count", 0) for c in clusters]) if clusters else 10
    
    ranked_clusters = []
    for cluster in clusters:
        ranked_cluster = impact_scorer(cluster, max_count=max_count, max_severity=5.0)
        ranked_clusters.append(ranked_cluster)
        
    task.payload["clusters"] = ranked_clusters
    task.status = "DONE"
    return task

def dedup_worker(task: A2AMessage) -> A2AMessage:
    """
    Checks ranked clusters against past roadmap.
    """
    themes = task.payload.get("clusters", [])
    past_roadmap = _load_past_roadmap()
    
    deduped_themes = roadmap_deduplicator(themes, past_roadmap)
    
    task.payload["themes"] = deduped_themes
    task.status = "DONE"
    return task
