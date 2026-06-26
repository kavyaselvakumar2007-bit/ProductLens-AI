import os
import uuid
import re
import csv
import json
import gradio as gr
import pandas as pd
import plotly.express as px
from main_agent import run_pipeline

os.makedirs("outputs", exist_ok=True)

# CSS for the premium dark enterprise theme
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body, .gradio-container {
    background-color: #09090B !important;
    color: #F8FAFC !important;
    font-family: 'Inter', sans-serif !important;
}

/* Glassmorphism Generic Card */
.glass-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 20px;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

/* KPI Cards Layout */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
}
.kpi-card {
    text-align: center;
    padding: 24px;
    border-radius: 16px;
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.6));
    border: 1px solid rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
}
.kpi-icon {
    font-size: 2em;
    margin-bottom: 8px;
}
.kpi-title {
    font-size: 0.85em;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
    font-weight: 600;
}
.kpi-value {
    font-size: 2.2em;
    font-weight: 700;
    color: #F8FAFC;
}

/* Theme Cards Layout */
.theme-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 24px;
}
.theme-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}
.theme-title-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
}
.theme-icon {
    font-size: 1.5em;
}
.theme-title {
    font-size: 1.2em;
    font-weight: 600;
    margin: 0;
}
.theme-score {
    font-size: 0.85em;
    color: #94A3B8;
    margin-top: 4px;
}

/* Priority Badges */
.badge {
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.75em;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge.high { background: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge.medium { background: rgba(245, 158, 11, 0.15); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge.low { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.3); }

/* Evidence & Actions */
.section-label {
    font-size: 0.85em;
    font-weight: 600;
    color: #94A3B8;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.evidence-box {
    background: rgba(15, 23, 42, 0.4);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.evidence-item {
    font-style: italic;
    font-size: 0.9em;
    color: #E2E8F0;
    margin-bottom: 8px;
    line-height: 1.4;
    padding-left: 12px;
    border-left: 2px solid rgba(255, 255, 255, 0.2);
}
.evidence-item:last-child { margin-bottom: 0; }

.actions-box {
    margin-top: 16px;
}
.action-item {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 0.9em;
    color: #F8FAFC;
}
.action-icon {
    color: #3B82F6;
    font-weight: bold;
}

/* Pipeline Flowchart */
.pipeline-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 16px;
    padding: 40px 20px;
}
.pipeline-node {
    width: 220px;
    text-align: center;
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    transition: all 0.3s ease;
}
.pipeline-node-title {
    font-weight: 600;
    font-size: 1.1em;
    margin-top: 8px;
}
.pipeline-node-icon {
    font-size: 2em;
}
.pipeline-node-status {
    font-size: 0.8em;
    color: #94A3B8;
    margin-top: 8px;
    font-weight: 500;
}
.pipeline-node.active {
    box-shadow: 0 0 25px rgba(59, 130, 246, 0.5);
    border-color: rgba(59, 130, 246, 0.8);
    animation: glow-pulse 2s infinite;
}
.pipeline-node.done {
    border-color: rgba(16, 185, 129, 0.5);
}
.pipeline-node.done .pipeline-node-status {
    color: #10B981;
}
.pipeline-arrow {
    font-size: 1.5em;
    color: rgba(255, 255, 255, 0.2);
}

@keyframes glow-pulse {
    0% { box-shadow: 0 0 10px rgba(59, 130, 246, 0.3); }
    50% { box-shadow: 0 0 30px rgba(59, 130, 246, 0.7); }
    100% { box-shadow: 0 0 10px rgba(59, 130, 246, 0.3); }
}

/* Custom Gradio Overrides */
div.gradio-container { max-width: 1400px !important; }
.tabs { background: transparent !important; }
.tab-nav { border-bottom: 1px solid rgba(255,255,255,0.1) !important; margin-bottom: 24px !important; }
button.selected { border-color: #3B82F6 !important; color: #3B82F6 !important; }
"""

THEME_ICONS = {
    "Performance Issues": "⚡",
    "UI & User Experience": "🎨",
    "Pricing & Billing": "💳",
    "Integrations": "🔗",
    "Onboarding Experience": "👋",
    "Security Enhancements": "🔒",
    "Notifications & Alerts": "🔔",
    "Customer Support": "🎧",
    "Feature Requests": "✨",
    "Miscellaneous Requests": "📦"
}

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

def strip_html(text: str) -> str:
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def build_kpi_html(run_summary: dict) -> str:
    total = run_summary.get("total_items", 0)
    themes = run_summary.get("themes_found", 0)
    conf = run_summary.get("avg_confidence", 0.0)
    time_ms = run_summary.get("total_latency_ms", 0.0)
    time_s = round(time_ms / 1000.0, 1)
    
    return f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon">📝</div>
            <div class="kpi-title">Total Feedback Items</div>
            <div class="kpi-value">{total}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-title">Themes Discovered</div>
            <div class="kpi-value">{themes}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🧠</div>
            <div class="kpi-title">Average Confidence</div>
            <div class="kpi-value">{int(conf * 100)}%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">⏱️</div>
            <div class="kpi-title">Processing Time</div>
            <div class="kpi-value">{time_s}s</div>
        </div>
    </div>
    """

def build_theme_cards_html(validated_themes: list[dict]) -> str:
    if not validated_themes:
        return "<div class='glass-card' style='text-align: center; color: #94A3B8;'>No themes found to display.</div>"
        
    sorted_themes = sorted(validated_themes, key=lambda x: x.get("priority_score", 0), reverse=True)
    cards = []
    
    for theme in sorted_themes:
        name = theme.get("theme_name", "Unknown")
        prio = theme.get("priority_label", "Low").lower()
        score = theme.get("priority_score", 0.0)
        icon = THEME_ICONS.get(name, "📌")
        
        # Build evidence list
        items = theme.get("items", [])[:3]
        evidence_html = "".join([f"<div class='evidence-item'>\"{item.get('text', '')}\"</div>" for item in items])
        
        # Build actions list
        actions = SUGGESTED_ACTIONS.get(name, ["Review feedback for potential actions"])
        actions_html = "".join([f"<div class='action-item'><span class='action-icon'>✓</span> {a}</div>" for a in actions])
        
        card = f"""
        <div class="glass-card">
            <div class="theme-header">
                <div class="theme-title-wrapper">
                    <span class="theme-icon">{icon}</span>
                    <div>
                        <h3 class="theme-title">{name}</h3>
                        <div class="theme-score">Confidence Score: {theme.get('confidence', 0.0)}</div>
                    </div>
                </div>
                <div class="badge {prio}">{prio} Priority</div>
            </div>
            
            <div class="section-label">Evidence Quotes</div>
            <div class="evidence-box">
                {evidence_html}
            </div>
            
            <div class="section-label">Suggested Actions</div>
            <div class="actions-box">
                {actions_html}
            </div>
        </div>
        """
        cards.append(card)
        
    return f"<div class='theme-grid'>{''.join(cards)}</div>"

def build_pipeline_html(state: str) -> str:
    # states: 'idle', 'processing', 'done'
    nodes = [
        {"id": "input", "title": "Data Ingestion", "icon": "📥", "desc": "CSV/Text Input"},
        {"id": "planner", "title": "Planner Agent", "icon": "🧠", "desc": "Task Routing"},
        {"id": "workers", "title": "Worker Agents", "icon": "⚙️", "desc": "Tag, Cluster, Rank"},
        {"id": "evaluator", "title": "Evaluator Agent", "icon": "⚖️", "desc": "Validation"},
        {"id": "report", "title": "Report Generator", "icon": "📊", "desc": "Dashboard Build"}
    ]
    
    html = '<div class="pipeline-container">'
    for i, node in enumerate(nodes):
        classes = "pipeline-node"
        status_text = "Pending"
        
        if state == "done":
            classes += " done"
            status_text = "Completed"
        elif state == "processing":
            classes += " active"
            status_text = "Processing..."
            
        html += f"""
        <div class="{classes}">
            <div class="pipeline-node-icon">{node['icon']}</div>
            <div class="pipeline-node-title">{node['title']}</div>
            <div class="pipeline-node-status">{status_text}</div>
        </div>
        """
        if i < len(nodes) - 1:
            html += '<div class="pipeline-arrow">➔</div>'
            
    html += '</div>'
    return html

from collections import Counter

def build_charts(validated_themes: list[dict]):
    if not validated_themes:
        return None, None
        
    # Safe theme counting using Counter
    theme_counter = Counter()
    for t in validated_themes:
        theme_name = t.get("theme_name", "Unknown")
        theme_counter[theme_name] += t.get("item_count", len(t.get("items", [])))
        
    theme_df = pd.DataFrame({
        "Theme": list(theme_counter.keys()),
        "Count": list(theme_counter.values())
    })
    
    # Debugging
    print("DEBUG validated_themes:", validated_themes)
    print("DEBUG theme_df:", theme_df)
    
    # Dark theme settings for Plotly
    template = "plotly_dark"
    paper_bgcolor = "#0B1020"
    plot_bgcolor = "#0B1020"
    marker_color = "#7C3AED"
    
    # Theme Distribution Chart
    if theme_df.empty:
        fig_theme = px.bar(title="Theme Distribution")
        fig_theme.add_annotation(text="No theme data available", showarrow=False, font=dict(size=20))
    else:
        fig_theme = px.bar(
            theme_df, 
            x='Count', 
            y='Theme', 
            orientation='h',
            title="Theme Distribution",
            template=template
        )
        fig_theme.update_traces(marker_color=marker_color)
        
    fig_theme.update_layout(
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    # Priority Distribution Chart
    df = pd.DataFrame(validated_themes)
    if df.empty or 'priority_label' not in df.columns:
        priority_counts = pd.DataFrame(columns=['Priority', 'Count'])
    else:
        priority_counts = df['priority_label'].value_counts().reset_index()
    priority_counts.columns = ['Priority', 'Count']
    
    color_map = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
    
    fig_prio = px.pie(
        priority_counts, 
        values='Count', 
        names='Priority', 
        hole=0.6,
        title="Priority Distribution",
        template=template,
        color='Priority',
        color_discrete_map=color_map
    )
    fig_prio.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig_theme, fig_prio

def process_feedback(csv_file, text_input, mock_json):
    session_id = str(uuid.uuid4())
    
    source_type = None
    data = None
    
    # 1. Input Validation
    if csv_file is not None:
        source_type = "csv"
        try:
            with open(csv_file.name, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) > 500:
                    yield (
                        "<div style='color:red;'>Error: CSV file exceeds 500 rows limit.</div>",
                        None, None, "", build_pipeline_html("idle"), "", "{}"
                    )
                    return
        except Exception as e:
            yield (
                f"<div style='color:red;'>Error reading CSV: {e}</div>",
                None, None, "", build_pipeline_html("idle"), "", "{}"
            )
            return
        data = csv_file.name
        
    elif text_input and text_input.strip():
        source_type = "text"
        data = strip_html(text_input)
        
    elif mock_json and mock_json != "None":
        source_type = "json"
        mock_data = [
            {"id": "m1", "text": "App crashes when I click the profile button", "source": "mock"},
            {"id": "m2", "text": "Please add a dark mode", "source": "mock"},
            {"id": "m3", "text": "Prices are too high!", "source": "mock"},
            {"id": "m4", "text": "UI is confusing on the dashboard", "source": "mock"}
        ]
        data = json.dumps(mock_data)
        
    else:
        yield (
            "<div style='color:red;'>Please provide feedback via CSV, Text, or select Mock JSON.</div>",
            None, None, "", build_pipeline_html("idle"), "", "{}"
        )
        return

    # Yield initial "Processing" state
    loading_kpi = "<div class='glass-card' style='text-align: center;'><h2>🚀 Initializing Agents...</h2></div>"
    yield (
        loading_kpi,
        None,
        None,
        "",
        build_pipeline_html("processing"),
        "Processing...",
        "{}"
    )

    # 2. Run Pipeline (Synchronous Call)
    try:
        result = run_pipeline(source_type, data, session_id)
    except Exception as e:
        yield (
            f"<div style='color:red;'>Pipeline failed: {e}</div>",
            None, None, "", build_pipeline_html("idle"), "", "{}"
        )
        return
        
    # 3. Process Results
    run_summary = result["run_summary"]
    validated_themes = result["validated_themes"]
    
    kpi_html = build_kpi_html(run_summary)
    theme_cards_html = build_theme_cards_html(validated_themes)
    fig_theme, fig_prio = build_charts(validated_themes)
    
    # Build Observability text
    obs_text = f"""
    ### Run Execution Summary
    - **Session ID:** `{session_id}`
    - **Total Processed:** {run_summary.get('total_items')} items
    - **Themes Found:** {run_summary.get('themes_found')}
    - **Themes Rejected:** {run_summary.get('themes_rejected')}
    - **Average Confidence:** {run_summary.get('avg_confidence')}
    - **Total Pipeline Latency:** {run_summary.get('total_latency_ms')} ms
    """
    
    obs_json = json.dumps(run_summary, indent=2)
    
    # Final yield
    yield (
        kpi_html,
        fig_theme,
        fig_prio,
        theme_cards_html,
        build_pipeline_html("done"),
        obs_text,
        obs_json
    )

def build_ui():
    with gr.Blocks(title="ProductLens AI", css=CUSTOM_CSS, theme=gr.themes.Base()) as demo:
        
        # Header Area
        with gr.Row():
            gr.HTML("""
                <div style="padding: 20px 0; display: flex; align-items: center; gap: 16px;">
                    <div style="font-size: 3em; background: linear-gradient(to right, #3B82F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">
                        ProductLens AI
                    </div>
                    <div style="padding-top: 10px; color: #94A3B8; font-size: 1.1em; border-left: 2px solid rgba(255,255,255,0.1); padding-left: 16px;">
                        Enterprise Feedback Intelligence
                    </div>
                </div>
            """)
            
        with gr.Tabs():
            # Tab 1: Main Dashboard
            with gr.Tab("📊 Dashboard & Reports"):
                # KPIs
                kpi_output = gr.HTML(build_kpi_html({}))
                
                # Charts
                with gr.Row():
                    theme_chart = gr.Plot(label="Theme Distribution")
                    priority_chart = gr.Plot(label="Priority Distribution")
                
                gr.Markdown("### Recommended Roadmap Actions")
                # Theme Cards
                theme_cards_output = gr.HTML("<div class='glass-card' style='text-align: center; color: #94A3B8;'>Upload data to generate report...</div>")
            
            # Tab 2: Agent Pipeline
            with gr.Tab("⚙️ Agent Pipeline"):
                gr.Markdown("### Multi-Agent Execution Flow")
                gr.Markdown("Watch the execution state of the specialized AI agents as they process the raw feedback into structured insights.")
                pipeline_output = gr.HTML(build_pipeline_html("idle"))
            
            # Tab 3: Data Ingestion
            with gr.Tab("📥 Data Ingestion"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### Upload Feedback Source")
                        csv_upload = gr.File(label="Upload CSV (Max 500 rows, columns: id, text, source, date)", file_types=[".csv"])
                        text_area = gr.TextArea(label="Paste Text (One feedback item per line)")
                        mock_json_dropdown = gr.Dropdown(choices=["None", "Load Mock Feedback Batch"], value="None", label="Or use Mock Data")
                        submit_btn = gr.Button("🚀 Run AI Agents", variant="primary", size="lg")
                    with gr.Column(scale=1):
                        gr.HTML("""
                            <div class="glass-card" style="margin-top: 40px;">
                                <h3 style="margin-top:0;">Supported Formats</h3>
                                <ul style="color:#94A3B8; font-size:0.9em; padding-left:16px;">
                                    <li>CSV exports from Zendesk/Jira</li>
                                    <li>Plain text copy-pasted</li>
                                    <li>JSON structured feedback</li>
                                </ul>
                                <div style="margin-top:16px; font-size:0.85em; color:#3B82F6;">Processing is completely local and private.</div>
                            </div>
                        """)
            
            # Tab 4: Observability
            with gr.Tab("🔍 Observability"):
                gr.Markdown("### Agent Run Metrics")
                obs_text_output = gr.Markdown("No runs executed yet.")
                with gr.Accordion("Raw Execution Logs (Developer View)", open=False):
                    obs_json_output = gr.JSON(label="JSON Trace")
                
        # Wiring
        submit_btn.click(
            fn=process_feedback,
            inputs=[csv_upload, text_area, mock_json_dropdown],
            outputs=[
                kpi_output,
                theme_chart,
                priority_chart,
                theme_cards_output,
                pipeline_output,
                obs_text_output,
                obs_json_output
            ]
        )
        
    return demo

if __name__ == "__main__":
    app = build_ui()
    app.launch()
