import os
from dotenv import load_dotenv

from memory.session_memory import SessionMemory, EpisodicMemory
from core.a2a_protocol import MessageBus
from core.observability import StructuredLogger
from tools.tools import feedback_ingester, report_generator
from agents.planner import run_planner
from agents.worker import tagger_worker, cluster_worker, ranker_worker, dedup_worker
from agents.evaluator import run_evaluator

# Ensure environment variables are loaded
load_dotenv()

def run_pipeline(source_type: str, data, session_id: str) -> dict:
    """
    Main orchestration pipeline for ProductLens AI.
    """
    # 1. Init Memory, MessageBus, Logger
    session_mem = SessionMemory()
    episodic_mem = EpisodicMemory()
    message_bus = MessageBus()
    logger = StructuredLogger()
    
    # 2. (Handled in functions) Load long_term_store.json
    
    # 3. Ingest Data
    raw_items = feedback_ingester(source_type, data)
    
    # 4. Save to session memory
    session_mem.save(session_id, "raw_items", raw_items)
    
    # 5. Call Planner
    task_ids = run_planner(raw_items, message_bus, logger)
    
    # 6. Call Worker Functions Sequentially
    
    # Tagger
    tagger_msg = message_bus.receive("tagger")
    if tagger_msg:
        # Tagger already has items payload from planner
        tagger_res = tagger_worker(tagger_msg)
    else:
        tagger_res = None
        
    # Cluster
    cluster_msg = message_bus.receive("cluster")
    if cluster_msg and tagger_res:
        cluster_msg.payload["items"] = tagger_res.payload.get("items", [])
        cluster_res = cluster_worker(cluster_msg)
    else:
        cluster_res = None
        
    # Ranker
    ranker_msg = message_bus.receive("ranker")
    if ranker_msg and cluster_res:
        ranker_msg.payload["clusters"] = cluster_res.payload.get("clusters", [])
        ranker_res = ranker_worker(ranker_msg)
    else:
        ranker_res = None
        
    # Dedup
    dedup_msg = message_bus.receive("dedup")
    if dedup_msg and ranker_res:
        dedup_msg.payload["clusters"] = ranker_res.payload.get("clusters", [])
        dedup_res = dedup_worker(dedup_msg)
    
    # 7. Collect Worker Results (Handled by wait_for_all in Evaluator)
    # The A2AMessages were modified in place and their status set to DONE.
    # The evaluator will scan the message_store for these task_ids.
    
    # 8. Call Evaluator
    eval_result = run_evaluator(task_ids, message_bus, logger, total_input_items=len(raw_items))
    validated_themes = eval_result["validated_themes"]
    
    # Fetch final summary stats from logger
    run_summary = logger.get_run_summary()
    
    # We add the rejected themes explicitly for the report generator
    run_summary["rejected_themes"] = eval_result["rejected_themes"]
    run_summary["timestamp"] = logger.in_memory_logs[-1]["timestamp"] if logger.in_memory_logs else "N/A"
    
    # 9. Call Report Generator
    report_md = report_generator(validated_themes, run_summary)
    
    # 10. Append run to episodic log
    episodic_mem.append_run({
        "session_id": session_id,
        "summary": run_summary,
        "themes": [t["theme_name"] for t in validated_themes]
    })
    
    # 11. Return
    return {
        "report_md": report_md,
        "run_summary": run_summary,
        "validated_themes": validated_themes
    }
