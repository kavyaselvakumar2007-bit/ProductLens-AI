import csv
import io
import json
import uuid
import difflib
from datetime import datetime
from typing import Any

def feedback_ingester(source_type: str, data: Any) -> list[dict]:
    """
    Ingest feedback from csv, text, or json and normalise it.
    Output: list of {id, text, source, date, raw}
    """
    normalised = []
    
    if source_type == "csv":
        # Check if data is a filepath
        if isinstance(data, str) and len(data) < 255 and ('/' in data or '\\' in data or data.endswith('.csv')):
            try:
                with open(data, 'r', encoding='utf-8') as file_obj:
                    data = file_obj.read()
            except Exception:
                pass # fallback to treating as string

        if isinstance(data, str):
             f = io.StringIO(data)
        elif hasattr(data, 'name'):
             f = open(data.name, 'r', encoding='utf-8')
        else:
             f = data
             
        reader = csv.DictReader(f)
        for row in reader:
            item_id = row.get("id", str(uuid.uuid4()))
            text = row.get("text", "")
            source = row.get("source", "csv")
            date = row.get("date", datetime.utcnow().isoformat())
            normalised.append({
                "id": item_id,
                "text": text,
                "source": source,
                "date": date,
                "raw": row
            })
            
    elif source_type == "text":
        lines = data.split("\n") if isinstance(data, str) else []
        for line in lines:
            if not line.strip():
                continue
            normalised.append({
                "id": str(uuid.uuid4()),
                "text": line.strip(),
                "source": "text",
                "date": datetime.utcnow().isoformat(),
                "raw": line
            })
            
    elif source_type == "json":
        parsed = json.loads(data) if isinstance(data, str) else data
        if not isinstance(parsed, list):
            parsed = [parsed]
        for item in parsed:
            item_id = item.get("id", str(uuid.uuid4()))
            text = item.get("text", "")
            source = item.get("source", "json")
            date = item.get("date", datetime.utcnow().isoformat())
            normalised.append({
                "id": item_id,
                "text": text,
                "source": source,
                "date": date,
                "raw": item
            })
            
    return normalised

def sentiment_scorer(text: str) -> dict:
    """
    Score sentiment using basic keywords.
    """
    text_lower = text.lower()
    positive_words = ["good", "great", "love", "excellent", "amazing", "awesome", "perfect", "like"]
    negative_words = ["bad", "terrible", "hate", "awful", "horrible", "crash", "bug", "issue", "slow", "fail"]
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    if pos_count > neg_count:
        return {"sentiment": "positive", "confidence": 0.8}
    elif neg_count > pos_count:
        return {"sentiment": "negative", "confidence": 0.8}
    else:
        return {"sentiment": "neutral", "confidence": 0.5}

def topic_tagger(text: str, taxonomy: list[str]) -> dict:
    """
    Tag text against taxonomy keywords using a robust mapping.
    """
    text_lower = text.lower()
    
    KEYWORD_MAP = {
        "Performance Issues": ["crash", "slow", "freeze", "load", "bug", "lag", "battery", "performance", "fast"],
        "UI & User Experience": ["ui", "layout", "font", "cluttered", "dark mode", "design", "ux", "interface"],
        "Pricing & Billing": ["price", "pricing", "cost", "expensive", "subscription", "tier", "pay", "billing"],
        "Integrations": ["integration", "slack", "teams", "api", "webhook", "sync", "connect"],
        "Onboarding Experience": ["onboarding", "tutorial", "confusing", "guide", "setup", "start", "welcome"],
        "Security Enhancements": ["security", "access control", "rbac", "auth", "login", "password", "permission"],
        "Notifications & Alerts": ["notification", "badge", "push", "alert", "email", "message"],
        "Customer Support": ["support", "help", "ticket", "response", "service", "contact"],
        "Feature Requests": ["feature", "add", "missing", "export", "pdf", "csv", "upload", "wish"]
    }
    
    matched = []
    
    for theme, keywords in KEYWORD_MAP.items():
        if theme in taxonomy:
            if any(kw in text_lower for kw in keywords):
                matched.append(theme)
            
    if not matched:
        return {"topic": "Miscellaneous Requests", "matched_keywords": []}
    
    # Return the first match as primary topic
    return {"topic": matched[0], "matched_keywords": matched}

def theme_clusterer(tagged_items: list[dict]) -> list[dict]:
    """
    Group tagged items by topic field.
    """
    clusters = {}
    
    for item in tagged_items:
        topic = item.get("topic", "Miscellaneous Requests")
        if topic not in clusters:
            clusters[topic] = {"theme_name": topic, "items": [], "item_count": 0, "severity_sum": 0.0}
        
        clusters[topic]["items"].append(item)
        clusters[topic]["item_count"] += 1
        clusters[topic]["severity_sum"] += float(item.get("severity", 3.0))
        
    result = []
    for topic, data in clusters.items():
        avg_severity = data["severity_sum"] / data["item_count"] if data["item_count"] > 0 else 0.0
        result.append({
            "theme_name": data["theme_name"],
            "items": data["items"],
            "item_count": data["item_count"],
            "avg_severity": avg_severity
        })
        
    return result

def impact_scorer(theme: dict, max_count: int = 10, max_severity: float = 5.0) -> dict:
    """
    Compute priority_score.
    priority_score = (frequency_normalized * 0.4) + (avg_severity_normalized * 0.4) + (recency_score * 0.2)
    """
    count = theme.get("item_count", 0)
    avg_severity = theme.get("avg_severity", 0.0)
    
    freq_norm = min(count / max(max_count, 1), 1.0)
    sev_norm = min(avg_severity / max(max_severity, 1.0), 1.0)
    
    # Simplified recency score
    recency_score = 0.8 
    
    priority_score = (freq_norm * 0.4) + (sev_norm * 0.4) + (recency_score * 0.2)
    
    if priority_score >= 0.7:
        priority_label = "High"
    elif priority_score >= 0.4:
        priority_label = "Medium"
    else:
        priority_label = "Low"
        
    theme["priority_score"] = round(priority_score, 3)
    theme["priority_label"] = priority_label
    
    return theme

def roadmap_deduplicator(themes: list[dict], past_roadmap: list[str]) -> list[dict]:
    """
    Deduplicate themes against past roadmap.
    """
    for theme in themes:
        theme_name = theme.get("theme_name", "")
        status = "new"
        
        for past_item in past_roadmap:
            similarity = difflib.SequenceMatcher(None, theme_name.lower(), past_item.lower()).ratio()
            if similarity > 0.6:
                status = "duplicate" # Can also map to "in_progress" based on logic, but default to duplicate here
                break
                
        theme["status"] = status
        
    return themes

def report_generator(validated_themes: list[dict], run_meta: dict) -> str:
    """
    Generate markdown report.
    """
    SUGGESTED_ACTIONS = {
        "Performance Issues": ["Investigate API latency", "Optimize database queries", "Add performance monitoring"],
        "UI & User Experience": ["Conduct user testing", "Review accessibility guidelines", "Refresh component library"],
        "Feature Requests": ["Prioritize in product backlog", "Gather more user requirements", "Evaluate technical feasibility"],
        "Security Enhancements": ["Conduct security audit", "Implement MFA/RBAC", "Review access logs"],
        "Onboarding Experience": ["Simplify setup steps", "Add interactive tooltips", "Create welcome video"],
        "Customer Support": ["Expand knowledge base", "Improve response times", "Add live chat option"],
        "Notifications & Alerts": ["Fix badge clearing logic", "Allow notification customization", "Add delivery receipts"],
        "Integrations": ["Review partner API docs", "Scope integration effort", "Survey users on tool usage"],
        "Pricing & Billing": ["Analyze tier usage", "Review competitor pricing", "Clarify billing terms on website"],
        "Miscellaneous Requests": ["Monitor for emerging trends", "Categorize in next review cycle"]
    }

    md = ["## ProductLens AI — Roadmap Recommendation\n"]
    
    # Executive Summary
    md.append("### Executive Summary")
    md.append(f"Processed **{run_meta.get('total_items', 0)}** items, finding **{run_meta.get('themes_found', 0)}** valid themes. "
              f"Average confidence: {run_meta.get('avg_confidence', 0.0):.2f}.\n")
              
    # Top Themes
    md.append("### Top Themes")
    md.append("| Theme | Priority | Score | Status |")
    md.append("|---|---|---|---|")
    
    # Sort themes by score descending
    sorted_themes = sorted(validated_themes, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    for theme in sorted_themes:
        name = theme.get("theme_name", "Unknown")
        prio = theme.get("priority_label", "Low")
        score = theme.get("priority_score", 0.0)
        status = theme.get("status", "new")
        md.append(f"| {name} | {prio} | {score} | {status} |")
        
    md.append("\n### Theme Details")
    for theme in sorted_themes:
        name = theme.get("theme_name", "Unknown")
        prio = theme.get("priority_label", "Low")
        
        md.append(f"#### Theme: {name}")
        md.append(f"**Priority:** {prio}\n")
        
        md.append("**Evidence Quotes:**")
        items = theme.get("items", [])[:3]
        for item in items:
            text = item.get("text", "")
            md.append(f"- \"{text}\"")
        md.append("")
        
        md.append("**Suggested Roadmap Actions:**")
        actions = SUGGESTED_ACTIONS.get(name, ["Review feedback for potential actions", "Assess impact on current roadmap"])
        for action in actions:
            md.append(f"- {action}")
        md.append("")
        
    md.append("### Rejected Themes")
    rejected = run_meta.get("rejected_themes", [])
    if rejected:
        for r in rejected:
            md.append(f"- {r}")
    else:
        md.append("None.")
        
    md.append("\n### Run Metadata")
    md.append(f"- Timestamp: {run_meta.get('timestamp', datetime.utcnow().isoformat())}")
    md.append(f"- Items processed: {run_meta.get('total_items', 0)}")
    md.append(f"- Valid themes: {run_meta.get('themes_found', 0)}")
    
    return "\n".join(md)

def summarizer(text: str, max_words: int) -> str:
    """
    Truncate text to max_words, append '...' if truncated.
    """
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return text
