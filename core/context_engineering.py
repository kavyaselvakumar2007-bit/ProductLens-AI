import json

def token_budget_check(prompt: str, max_tokens: int) -> str:
    """
    Check if a prompt is within the token budget.
    If over budget, truncate the feedback list portion and add '[truncated]' marker.
    """
    words = prompt.split()
    estimated_tokens = len(words) * 1.3
    
    if estimated_tokens <= max_tokens:
        return prompt
        
    # Naive truncation strategy: we just cut the prompt to approx the max words
    # and append [truncated]. In a real app, we'd specifically target the feedback list.
    allowed_words = int(max_tokens / 1.3)
    truncated_prompt = " ".join(words[:allowed_words]) + "\n\n...[truncated]"
    return truncated_prompt

def build_prompt(agent_role: str, payload: dict, taxonomy: list) -> str:
    """
    Build a role-specific prompt for the Gemini API.
    """
    if agent_role == "planner":
        items = payload.get("items", [])
        return f"""You are the Planner Agent. Your job is to analyze this batch of {len(items)} feedback items and decide how to route them.
Taxonomy available: {json.dumps(taxonomy)}

Summary of feedback items:
{json.dumps([{'id': i.get('id'), 'text': i.get('text')} for i in items][:10], indent=2)}
...

Assign tasks to the appropriate workers. Note: The actual dispatching is handled by the system.
Your output should briefly summarize the data mix and confirm readiness to dispatch tasks.
"""

    elif agent_role == "tagger":
        item = payload.get("item", {})
        return f"""You are the Tagger Agent. Analyze the following feedback item.

Feedback: "{item.get('text', '')}"

You must output STRICT JSON format exactly like this example:
{{
  "id": "12345",
  "text": "The app crashes on startup",
  "sentiment": "negative",
  "topic": "crash",
  "severity": 5
}}

Available taxonomy topics: {json.dumps(taxonomy)}
Output ONLY the JSON and nothing else.
"""

    elif agent_role == "cluster":
        items = payload.get("items", [])
        return f"""You are the Cluster Agent. Review the following tagged feedback items.

{json.dumps(items, indent=2)}

Group these items into logical themes. Give each cluster a short, descriptive name (e.g. "App Startup Crashes").
If any cluster has fewer than 2 items, merge it into "Other".
"""

    elif agent_role == "ranker":
        clusters = payload.get("clusters", [])
        return f"""You are the Ranker Agent. Rank the following clusters based on importance.

{json.dumps(clusters, indent=2)}

Scoring rubric: 
- priority_score = (frequency_normalized * 0.4) + (avg_severity_normalized * 0.4) + (recency_score * 0.2)
Return your justification and ranking.
"""

    elif agent_role == "dedup":
        themes = payload.get("themes", [])
        past_roadmap = payload.get("past_roadmap", [])
        return f"""You are the Deduplication Agent. Compare these new themes:
{json.dumps([t.get('theme_name') for t in themes], indent=2)}

Against the past roadmap:
{json.dumps(past_roadmap, indent=2)}

Identify which new themes are "new", "duplicate", or "in_progress".
"""

    elif agent_role == "evaluator":
        return f"""You are the Evaluator Agent. Check the outputs from all workers for quality.

Validation Checklist:
1. Coverage check: Every input feedback item must appear in at least one cluster.
2. Hallucination check: Every theme must cite at least 2 real feedback item IDs as evidence.
3. Confidence scoring: Calculate confidence. Reject themes with confidence < 0.4.

Data provided in payload:
{json.dumps({k: str(v)[:100] + '...' for k, v in payload.items()}, indent=2)}
"""

    return "System Prompt: Proceed with your task."
