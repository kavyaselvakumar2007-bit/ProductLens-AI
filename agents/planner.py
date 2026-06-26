import json
import time
import google.generativeai as genai
from core.a2a_protocol import A2AMessage, MessageBus
from core.context_engineering import build_prompt, token_budget_check
from core.observability import StructuredLogger

def load_taxonomy(path: str = "memory/long_term_store.json") -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("product_taxonomy", [])
    except Exception:
        return []

def run_planner(raw_feedback: list[dict], message_bus: MessageBus, logger: StructuredLogger) -> list[str]:
    """
    Planner agent: analyzes feedback and builds task manifest.
    Returns the list of msg_ids dispatched.
    """
    start_time = time.time()
    taxonomy = load_taxonomy()
    
    # 1. Context Engineering
    prompt = build_prompt("planner", {"items": raw_feedback}, taxonomy)
    prompt = token_budget_check(prompt, max_tokens=2000)
    
    # 2. LLM Call (Optional/Fallback)
    # Even if LLM fails, we proceed with the rule-based dispatch
    token_count = len(prompt.split()) * 1.3
    try:
        # Assuming genai is configured in main_agent or app
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        notes = "Planner used LLM."
    except Exception as e:
        notes = f"Planner fallback (LLM failed: {e})."
        
    # 3. Build Task Manifest
    msg_ids = []
    
    # Tagger task
    tagger_msg = A2AMessage(sender="planner", recipient="tagger", task_type="TAG", payload={"items": raw_feedback})
    message_bus.send(tagger_msg)
    msg_ids.append(tagger_msg.msg_id)
    
    # Cluster task (payload initially empty or we just pass the items knowing it will be overwritten)
    cluster_msg = A2AMessage(sender="planner", recipient="cluster", task_type="CLUSTER", payload={})
    message_bus.send(cluster_msg)
    msg_ids.append(cluster_msg.msg_id)
    
    # Ranker task
    ranker_msg = A2AMessage(sender="planner", recipient="ranker", task_type="RANK", payload={})
    message_bus.send(ranker_msg)
    msg_ids.append(ranker_msg.msg_id)
    
    # Dedup task
    dedup_msg = A2AMessage(sender="planner", recipient="dedup", task_type="DEDUP", payload={})
    message_bus.send(dedup_msg)
    msg_ids.append(dedup_msg.msg_id)
    
    # 4. Observability Log
    latency_ms = (time.time() - start_time) * 1000
    logger.log_event(
        agent="planner", 
        task_type="PLAN", 
        status="DONE", 
        latency_ms=latency_ms, 
        token_count=int(token_count), 
        notes=notes
    )
    
    return msg_ids
