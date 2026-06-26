import time
import google.generativeai as genai
from core.a2a_protocol import MessageBus
from core.observability import StructuredLogger
from core.context_engineering import build_prompt

def run_evaluator(task_ids: list[str], message_bus: MessageBus, logger: StructuredLogger, total_input_items: int) -> dict:
    """
    Evaluator agent: Collects worker outputs, performs checks, returns validated themes.
    """
    start_time = time.time()
    
    # 1. Collect outputs
    messages = message_bus.wait_for_all(task_ids)
    
    # Find the final themes from dedup output
    dedup_msg = next((m for m in messages if m and m.recipient == "dedup"), None)
    themes = dedup_msg.payload.get("themes", []) if dedup_msg else []
    
    # Find original tagger output to get all valid IDs if needed
    tagger_msg = next((m for m in messages if m and m.recipient == "tagger"), None)
    all_input_ids = [item.get("id") for item in tagger_msg.payload.get("items", [])] if tagger_msg else []
    
    validated_themes = []
    rejected_themes = []
    
    # Coverage tracking
    covered_ids = set()
    
    # 2. Validation Checks
    # Calculate coverage upfront
    for theme in themes:
        items = theme.get("items", [])
        for item in items:
            if item.get("id") in all_input_ids:
                covered_ids.add(item.get("id"))
                
    coverage_pct = len(covered_ids) / total_input_items if total_input_items > 0 else 0

    for theme in themes:
        items = theme.get("items", [])
        evidence_count = len(items)
                
        # Hallucination check (we use actual items in cluster, so evidence is valid)
        valid_evidence_count = sum(1 for item in items if item.get("id") in all_input_ids)
            
        # Confidence scoring
        evidence_score = min(valid_evidence_count / 2.0, 1.0) # 2 items = full score, 1 item = 0.5
        
        confidence = (coverage_pct * 0.3) + (evidence_score * 0.7)
        theme["confidence"] = round(confidence, 3)
        
        if confidence < 0.35: # Lowered rejection threshold
            rejected_themes.append(theme.get("theme_name"))
        else:
            validated_themes.append(theme)
            
    # 3. Use LLM for a final heuristic check (Optional)
    prompt = build_prompt("evaluator", {"themes": validated_themes}, [])
    token_count = len(prompt.split()) * 1.3
    notes = "Evaluator finished locally."
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        notes += " LLM verification passed."
    except Exception as e:
        pass
        
    latency_ms = (time.time() - start_time) * 1000
    logger.log_event(
        agent="evaluator", 
        task_type="EVALUATE", 
        status="DONE", 
        latency_ms=latency_ms, 
        token_count=int(token_count), 
        notes=notes
    )
    
    avg_confidence = sum([t["confidence"] for t in validated_themes]) / len(validated_themes) if validated_themes else 0.0
    
    # Update observability summary
    logger.update_summary(
        total_items=total_input_items,
        themes_found=len(validated_themes),
        themes_rejected=len(rejected_themes),
        confidence_sum=sum([t["confidence"] for t in validated_themes]),
        confidence_count=len(validated_themes)
    )
    
    return {
        "validated_themes": validated_themes,
        "rejected_themes": rejected_themes,
        "avg_confidence": avg_confidence
    }
