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

# Advanced CSS for the Ultra-Premium SaaS interface
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

/* Base & Animated Orb Background */
body, .gradio-container {
    background-color: #000000 !important;
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.15), transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(236, 72, 153, 0.12), transparent 40%),
        radial-gradient(circle at 50% -20%, rgba(56, 189, 248, 0.1), transparent 50%);
    color: #F8FAFC !important;
    font-family: 'Inter', sans-serif !important;
    margin: 0;
    padding: 0;
}

/* Animations */
@keyframes fade-in-up {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes pulse-orb {
    0% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
    100% { transform: scale(1); opacity: 0.5; }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

/* Hero Section */
.hero-container {
    text-align: center;
    padding: 60px 20px 40px;
    animation: fade-in-up 0.8s ease-out;
    position: relative;
    z-index: 10;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 16px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #E2E8F0;
    border-radius: 999px;
    font-size: 0.85em;
    font-weight: 500;
    margin-bottom: 24px;
    letter-spacing: 0.05em;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}
.hero-badge span { margin-right: 8px; }
.hero-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 4.5em;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 0 0 16px 0;
    line-height: 1.1;
    background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 1.2em;
    color: #94A3B8;
    max-width: 650px;
    margin: 0 auto;
    line-height: 1.6;
    font-weight: 300;
}

/* Pill-Style Navigation Override */
.tabs { background: transparent !important; border: none !important; }
.tab-nav {
    border: none !important;
    display: flex !important;
    justify-content: center !important;
    gap: 12px !important;
    margin-bottom: 40px !important;
    padding: 8px !important;
    background: rgba(255, 255, 255, 0.02) !important;
    border-radius: 999px !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
}
.tab-nav button {
    border: none !important;
    background: transparent !important;
    color: #94A3B8 !important;
    padding: 10px 24px !important;
    border-radius: 999px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s ease !important;
}
.tab-nav button:hover {
    color: #F8FAFC !important;
    background: rgba(255, 255, 255, 0.05) !important;
}
.tab-nav button.selected {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 15px rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* Glassmorphism Generic Card */
.glass-card {
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 32px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease;
    margin-bottom: 24px;
    animation: fade-in-up 0.6s ease-out backwards;
}
.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 30px rgba(99, 102, 241, 0.05) inset;
    border-color: rgba(255, 255, 255, 0.1);
}

/* KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}
.kpi-card {
    position: relative;
    overflow: hidden;
    padding: 28px;
    border-radius: 20px;
    background: linear-gradient(165deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(16px);
    transition: all 0.4s ease;
    animation: fade-in-up 0.5s ease-out backwards;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    opacity: 0;
    transition: opacity 0.4s ease;
}
.kpi-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    border-color: rgba(255,255,255,0.12);
}
.kpi-card:hover::before { opacity: 1; }
.kpi-icon {
    font-size: 1.8em;
    margin-bottom: 16px;
    display: inline-block;
    padding: 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
}
.kpi-title {
    font-size: 0.85em;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
    font-weight: 600;
}
.kpi-value {
    font-size: 2.8em;
    font-weight: 700;
    color: #FFFFFF;
    font-family: 'Outfit', sans-serif;
    line-height: 1;
}

/* Skeleton Loading State */
.skeleton-card {
    padding: 24px;
    border-radius: 20px;
    background: rgba(30, 41, 59, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.03);
}
.skeleton-line {
    height: 20px;
    border-radius: 10px;
    background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite linear;
    margin-bottom: 16px;
}

/* Theme Cards Grid */
.theme-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 24px;
}
.theme-card {
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 24px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    animation: fade-in-up 0.6s ease-out backwards;
}
.theme-card:hover {
    transform: translateY(-4px) scale(1.01);
    border-color: rgba(255,255,255,0.1);
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}
.theme-card-top-border {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.theme-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
}
.theme-title-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
}
.theme-icon { font-size: 1.5em; }
.theme-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.2em;
    font-weight: 600;
    margin: 0;
    color: #F8FAFC;
}
.theme-score {
    font-size: 0.8em;
    color: #64748B;
    margin-top: 4px;
}

/* Badges */
.badge {
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.7em;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.badge.high { background: rgba(239, 68, 68, 0.1); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.2); }
.badge.medium { background: rgba(245, 158, 11, 0.1); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.2); }
.badge.low { background: rgba(16, 185, 129, 0.1); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.2); }

/* Inset Evidence Quotes */
.evidence-box {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.02);
}
.evidence-item {
    font-style: italic;
    font-size: 0.85em;
    color: #CBD5E1;
    margin-bottom: 12px;
    line-height: 1.6;
    padding-left: 14px;
    border-left: 2px solid rgba(255,255,255,0.2);
}
.evidence-item:last-child { margin-bottom: 0; }

/* Show More Details */
details {
    cursor: pointer;
}
details summary {
    font-size: 0.85em;
    font-weight: 600;
    color: #60A5FA;
    outline: none;
    margin-bottom: 12px;
}
details[open] summary { color: #94A3B8; }
.action-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
    font-size: 0.9em;
    color: #E2E8F0;
}
.action-icon {
    color: #10B981;
    font-size: 1.1em;
    margin-top: 2px;
}

/* Agent Pipeline Diagram */
.pipeline-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30px;
    padding: 40px 0;
}
@media(min-width: 768px) {
    .pipeline-container {
        flex-direction: row;
        justify-content: center;
    }
}
.pipeline-node {
    width: 200px;
    text-align: center;
    padding: 24px;
    border-radius: 20px;
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    position: relative;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(12px);
}
.pipeline-node-icon { font-size: 2.5em; margin-bottom: 12px; }
.pipeline-node-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 1.1em;
    color: #F8FAFC;
}
.pipeline-node-status {
    font-size: 0.75em;
    color: #94A3B8;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.pipeline-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255,255,255,0.1);
    font-size: 1.5em;
    transform: rotate(90deg);
}
@media(min-width: 768px) {
    .pipeline-arrow { transform: rotate(0deg); }
}

/* Node States */
.pipeline-node.active {
    background: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 0 30px rgba(59, 130, 246, 0.2), inset 0 0 20px rgba(59, 130, 246, 0.1);
    transform: scale(1.05);
}
.pipeline-node.done {
    border-color: rgba(16, 185, 129, 0.3);
}
.pipeline-node.done .pipeline-node-status { color: #10B981; }

/* Empty State / Loading */
.empty-state {
    text-align: center;
    padding: 80px 20px;
    color: #64748B;
}
.empty-icon { font-size: 4em; margin-bottom: 20px; opacity: 0.4; }
.empty-state h2 { font-family: 'Outfit', sans-serif; color: #E2E8F0; }

.loading-container {
    text-align: center;
    padding: 60px 20px;
}
.spinner {
    width: 40px; height: 40px;
    border: 3px solid rgba(255,255,255,0.1);
    border-radius: 50%;
    border-top-color: #3B82F6;
    animation: spin 1s ease-in-out infinite;
    margin: 0 auto 20px;
}
@keyframes spin { to { transform: rotate(360deg); } }

#dev-logs-panel {
background: #0D1117 !important;
border-radius: 16px !important;
font-family: 'JetBrains Mono', monospace !important;
font-size: 12.5px !important;
color: #79C0FF !important;
border: 1px solid rgba(255,255,255,0.07) !important;
}
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

def build_empty_state() -> str:
    return """
    <div class="empty-state">
        <div class="empty-icon">📂</div>
        <h2>Awaiting Intelligence</h2>
        <p>Upload feedback in the Data Ingestion tab to activate autonomous agents.</p>
    </div>
    """

def build_skeleton_kpi() -> str:
    return """
    <div class="kpi-grid">
        <div class="skeleton-card"><div class="skeleton-line" style="width: 40px; height: 40px;"></div><div class="skeleton-line"></div><div class="skeleton-line" style="height: 40px;"></div></div>
        <div class="skeleton-card"><div class="skeleton-line" style="width: 40px; height: 40px;"></div><div class="skeleton-line"></div><div class="skeleton-line" style="height: 40px;"></div></div>
        <div class="skeleton-card"><div class="skeleton-line" style="width: 40px; height: 40px;"></div><div class="skeleton-line"></div><div class="skeleton-line" style="height: 40px;"></div></div>
        <div class="skeleton-card"><div class="skeleton-line" style="width: 40px; height: 40px;"></div><div class="skeleton-line"></div><div class="skeleton-line" style="height: 40px;"></div></div>
    </div>
    """

def build_kpi_html(run_summary: dict) -> str:
    if not run_summary:
        return build_empty_state()
        
    total = run_summary.get("total_items", 0)
    themes = run_summary.get("themes_found", 0)
    conf = run_summary.get("avg_confidence", 0.0)
    time_ms = run_summary.get("total_latency_ms", 0.0)
    time_s = round(time_ms / 1000.0, 1)
    
    # Delay animation slightly for sequence effect
    return f"""
    <div class="kpi-grid">
        <div class="kpi-card" style="animation-delay: 0.1s;">
            <div class="kpi-icon">📝</div>
            <div class="kpi-title">Items Processed</div>
            <div class="kpi-value">{total}</div>
        </div>
        <div class="kpi-card" style="animation-delay: 0.2s;">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-title">Themes Identified</div>
            <div class="kpi-value">{themes}</div>
        </div>
        <div class="kpi-card" style="animation-delay: 0.3s;">
            <div class="kpi-icon">🧠</div>
            <div class="kpi-title">AI Confidence</div>
            <div class="kpi-value">{int(conf * 100)}%</div>
        </div>
        <div class="kpi-card" style="animation-delay: 0.4s;">
            <div class="kpi-icon">⏱️</div>
            <div class="kpi-title">Pipeline Latency</div>
            <div class="kpi-value">{time_s}s</div>
        </div>
    </div>
    """

def build_observability_html(run_summary: dict) -> str:
    if not run_summary:
        return build_empty_state()
        
    total = run_summary.get("total_items", 0)
    found = run_summary.get("themes_found", 0)
    rej = run_summary.get("themes_rejected", 0)
    time_ms = run_summary.get("total_latency_ms", 0.0)
    time_s = round(time_ms / 1000.0, 1)
    
    return f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Ingested Items</div>
            <div class="kpi-value">{total}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Validated Themes</div>
            <div class="kpi-value" style="color:#34D399;">{found}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Rejected (Hallucinations)</div>
            <div class="kpi-value" style="color:#F87171;">{rej}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Total Execution</div>
            <div class="kpi-value">{time_s}s</div>
        </div>
    </div>
    """

def build_theme_cards_html(validated_themes: list[dict]) -> str:
    if not validated_themes:
        return build_empty_state()
        
    sorted_themes = sorted(validated_themes, key=lambda x: x.get("priority_score", 0), reverse=True)
    cards = []
    
    for i, theme in enumerate(sorted_themes):
        name = theme.get("theme_name", "Unknown")
        prio = theme.get("priority_label", "Low").lower()
        icon = THEME_ICONS.get(name, "📌")
        
        # Build evidence list
        items = theme.get("items", [])[:2] # Keep it smaller and cleaner
        evidence_html = "".join([f"<div class='evidence-item'>\"{item.get('text', '')}\"</div>" for item in items])
        
        # Build actions list inside a <details> element for "Show More" functionality
        actions = SUGGESTED_ACTIONS.get(name, ["Review feedback for potential actions"])
        actions_html = "".join([f"<div class='action-item'><span class='action-icon'>✓</span> <span>{a}</span></div>" for a in actions])
        
        # Priority Border Colors
        border_color = "#10B981" # Low
        if prio == "high": border_color = "#EF4444"
        elif prio == "medium": border_color = "#F59E0B"
        
        delay = i * 0.1
        card = f"""
        <div class="theme-card" style="animation-delay: {delay}s;">
            <div class="theme-card-top-border" style="background: {border_color};"></div>
            <div class="theme-header">
                <div class="theme-title-wrapper">
                    <span class="theme-icon">{icon}</span>
                    <div>
                        <h3 class="theme-title">{name}</h3>
                        <div class="theme-score">Confidence: {int(theme.get('confidence', 0.0) * 100)}%</div>
                    </div>
                </div>
                <div class="badge {prio}">{prio}</div>
            </div>
            
            <div class="evidence-box">
                {evidence_html}
            </div>
            
            <details>
                <summary>Suggested Actions</summary>
                <div style="padding-top: 8px;">
                    {actions_html}
                </div>
            </details>
        </div>
        """
        cards.append(card)
        
    return f"<div class='theme-grid'>{''.join(cards)}</div>"

def build_pipeline_html(state: str) -> str:
    nodes = [
        {"id": "input", "title": "Data Ingestion", "icon": "📥"},
        {"id": "planner", "title": "Planner Agent", "icon": "🧠"},
        {"id": "workers", "title": "Worker Agents", "icon": "⚙️"},
        {"id": "evaluator", "title": "Evaluator Agent", "icon": "⚖️"},
        {"id": "report", "title": "Dashboard Gen", "icon": "📊"}
    ]
    
    html = '<div class="pipeline-container">'
    for i, node in enumerate(nodes):
        classes = "pipeline-node"
        status_text = "Pending"
        
        if state == "done":
            classes += " done"
            status_text = "Completed"
        elif state == "processing":
            # Just light up the middle nodes for a generic processing state
            if i in [1, 2, 3]:
                classes += " active"
                status_text = "Processing..."
            elif i == 0:
                classes += " done"
                status_text = "Completed"
            
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

def build_charts(validated_themes: list[dict]):
        
    themes = []
    counts = []
    for t in validated_themes:
        theme_name = t.get("theme_name", "Unknown")
        count = max(t.get("item_count", 0), len(t.get("items", [])), 1)
        themes.append(theme_name)
        counts.append(count)
        
    theme_df = pd.DataFrame({"Theme": themes, "Count": counts})
    
    # Ultra-premium dark Plotly settings
    template = "plotly_dark"
    bg_color = "rgba(0,0,0,0)"
    font_family = "Inter, sans-serif"
    
    if theme_df.empty:
        fig_theme = px.bar(title="Theme Distribution")
        fig_theme.add_annotation(text="No data", showarrow=False)
    else:
        fig_theme = px.bar(
            theme_df, x='Count', y='Theme', orientation='h',
            title="Theme Distribution", template=template
        )
        fig_theme.update_traces(
            marker_color="#818CF8", 
            marker_line_color='rgba(255,255,255,0.1)', 
            marker_line_width=1,
            
        )
        
    fig_theme.update_layout(
        bargap=0.35,
        bargroupgap=0.15,
        plot_bgcolor=bg_color, 
        paper_bgcolor=bg_color,
        font=dict(family=font_family, color="#94A3B8"),
        title_font=dict(family="Outfit, sans-serif", size=18, color="#F8FAFC"),
        height=380, showlegend=False,
        margin=dict(l=10, r=20, t=60, b=20),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=""),
        yaxis=dict(showgrid=False, title="")
    )
    
    df = pd.DataFrame(validated_themes)
    if df.empty or 'priority_label' not in df.columns:
        priority_counts = pd.DataFrame(columns=['Priority', 'Count'])
    else:
        priority_counts = df['priority_label'].value_counts().reset_index()
    priority_counts.columns = ['Priority', 'Count']
    
    color_map = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
    
    if priority_counts.empty:
        fig_prio = px.pie(title="Priority Breakdown")
        fig_prio.add_annotation(text="No data", showarrow=False)
    else:
        fig_prio = px.pie(
            priority_counts, values='Count', names='Priority', hole=0.75,
            title="Priority Breakdown", template=template,
            color='Priority', color_discrete_map=color_map
        )
        fig_prio.update_traces(textinfo='percent', hoverinfo='label+percent', marker=dict(line=dict(color='#0F172A', width=2)))
        
    fig_prio.update_layout(
        plot_bgcolor=bg_color, paper_bgcolor=bg_color,
        font=dict(family=font_family, color="#94A3B8"),
        title_font=dict(family="Outfit, sans-serif", size=18, color="#F8FAFC"),
        height=380, margin=dict(l=10, r=10, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    
    return fig_theme, fig_prio

def process_feedback(csv_file, text_input, mock_json, progress=gr.Progress()):
    progress(0, desc="Initializing pipeline...")
    session_id = str(uuid.uuid4())
    source_type = None
    data = None
    
    empty_kpi = build_empty_state()
    empty_cards = build_empty_state()
    empty_obs = build_empty_state()
    f1_empty, f2_empty = build_charts([])
    
    def error_card(msg):
        return f"<div style='color:#EF4444; border:1px solid #EF4444;' class='glass-card'>⚠️ Error: {msg}</div>"
        
    try:
        # 1. Validation
        if csv_file is not None:
            if os.path.getsize(csv_file.name) / (1024*1024) > 5.0:
                yield (error_card("File exceeds 5MB limit."), f1_empty, f2_empty, empty_cards, build_pipeline_html("idle"), empty_obs, {})
                return
            source_type = "csv"
            try:
                with open(csv_file.name, 'r', encoding='utf-8') as f:
                    rows = list(csv.reader(f))
                    if len(rows) > 500:
                        yield (error_card("CSV exceeds 500 rows limit."), f1_empty, f2_empty, empty_cards, build_pipeline_html("idle"), empty_obs, {})
                        return
            except Exception as e:
                yield (error_card(str(e)), f1_empty, f2_empty, empty_cards, build_pipeline_html("idle"), empty_obs, {})
                return
            data = csv_file.name
            
        elif text_input and text_input.strip():
            source_type = "text"
            data = strip_html(text_input)
        elif mock_json and mock_json != "None":
            source_type = "json"
            data = json.dumps([
                {"id": "m1", "text": "App crashes on login.", "source": "mock"},
                {"id": "m2", "text": "Need dark mode.", "source": "mock"},
                {"id": "m3", "text": "Pricing is too high.", "source": "mock"}
            ])
        else:
            yield (error_card("Please provide feedback."), f1_empty, f2_empty, empty_cards, build_pipeline_html("idle"), empty_obs, {})
            return

        # Loading State
        loading_html = """
        <div class="loading-container">
            <div class="spinner"></div>
            <h2 style="font-family:'Outfit', sans-serif; color:#F8FAFC;">AI Agents analyzing feedback...</h2>
            <p style="color:#94A3B8;">Orchestrating Planner, Workers, and Evaluator via MessageBus.</p>
        </div>
        """
        
        yield (
            build_skeleton_kpi(),
            f1_empty,
            f2_empty,
            loading_html,
            build_pipeline_html("processing"),
            build_skeleton_kpi(),
            {}
        )

        # 2. Pipeline Execution
        result = run_pipeline(source_type, data, session_id)
            
        # 3. Render Results
        rs = result.get("run_summary", {})
        vt = result.get("validated_themes", [])
        
        # Temporary debugging
        print("validated_themes:", vt)
        print("run_summary:", rs)
        
        kpi_html = build_kpi_html(rs)
        cards_html = build_theme_cards_html(vt)
        f1, f2 = build_charts(vt)
        obs_html = build_observability_html(rs)
        
        return_values = (
            kpi_html, f1, f2, cards_html, 
            build_pipeline_html("done"), 
            obs_html, rs
        )
        print("Returning outputs:", len(return_values))
        yield return_values

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        
        error_html = f'''
        <div class="glass-card" style="border-color:#EF4444;">
            <h3 style="color:#EF4444;">⚠ Analysis Error</h3>
            <p>{str(e)}</p>
        </div>
        '''
        
        yield (error_html, f1_empty, f2_empty, empty_cards, build_pipeline_html("idle"), empty_obs, {})

def build_ui():
    with gr.Blocks(title="ProductLens AI", css=CUSTOM_CSS, theme=gr.themes.Base()) as demo:
        
        # Hero Section
        gr.HTML("""
            <div class="hero-container">
                <div class="hero-badge"><span>🚀</span> Autonomous AI Agents for Business</div>
                <h1 class="hero-title">ProductLens AI</h1>
                <p class="hero-subtitle">Transform unstructured customer feedback into a ranked, evidence-backed product roadmap using a network of specialized AI agents.</p>
            </div>
        """)
            
        with gr.Tabs():
            # Tab 1: Main Dashboard
            with gr.Tab("📊 Dashboard"):
                kpi_output = gr.HTML(build_empty_state())
                with gr.Row():
                    theme_chart = gr.Plot()
                    priority_chart = gr.Plot()
                
                gr.Markdown("<h3 style='font-family:Outfit; margin-top:20px;'>Theme Recommendations</h3>")
                theme_cards_output = gr.HTML(build_empty_state())
            
            # Tab 2: Agent Pipeline
            with gr.Tab("⚙️ Agent Pipeline"):
                gr.Markdown("<h3 style='text-align:center; font-family:Outfit;'>Multi-Agent Architecture</h3>")
                pipeline_output = gr.HTML(build_pipeline_html("idle"))
            
            # Tab 3: Data Ingestion
            with gr.Tab("📥 Data Ingestion"):
                with gr.Row():
                    with gr.Column(scale=2):
                        csv_upload = gr.File(label="Upload CSV (< 5MB, Max 500 rows)", file_types=[".csv", ".txt"])
                        text_area = gr.TextArea(label="Paste Text (One item per line)")
                        mock_json_dropdown = gr.Dropdown(choices=["None", "Load Mock Feedback Batch"], value="None", label="Use Mock Data")
                        submit_btn = gr.Button("🚀 Run Pipeline", variant="primary", size="lg")
                    with gr.Column(scale=1):
                        gr.HTML("""
                            <div class="glass-card">
                                <h3 style="margin-top:0;">Secure Local Processing</h3>
                                <p style="color:#94A3B8; font-size:0.9em; line-height:1.6;">
                                    Data is isolated, sanitized, and passed directly into the Agent MessageBus. No databases are used.
                                </p>
                            </div>
                        """)
            
            # Tab 4: Observability
            with gr.Tab("🔍 Observability"):
                gr.Markdown("<h3 style='font-family:Outfit;'>Executive Telemetry</h3>")
                obs_text_output = gr.HTML(build_empty_state())
                with gr.Accordion("🛠 Developer Logs", open=False):
                    obs_json_output = gr.JSON(label="", elem_id="dev-logs-panel")
                
        # Wiring
        submit_btn.click(
            fn=process_feedback,
            inputs=[csv_upload, text_area, mock_json_dropdown],
            outputs=[
                kpi_output, theme_chart, priority_chart, theme_cards_output,
                pipeline_output, obs_text_output, obs_json_output
            ]
        )
        
    return demo

if __name__ == "__main__":
    app = build_ui()
    app.launch()
