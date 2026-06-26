# ProductLens AI 🚀
Transform customer feedback into actionable product roadmap recommendations using autonomous AI agents.

## Overview
ProductLens AI is an end-to-end multi-agent SaaS application built for product managers. It takes raw feedback (CSV, Text, JSON), processes it through specialized autonomous agents (Planner, Worker, Evaluator), and outputs a dynamic, business-friendly dashboard outlining critical themes, confidence scores, and suggested roadmap actions.

## Features
- **Multi-Agent Orchestration**: Zero-dependency `MessageBus` coordinating independent LLM agents.
- **Premium Enterprise UI**: Glassmorphism, animations, and dark-theme SaaS dashboard using Gradio.
- **Analytics & Observability**: Interactive Plotly charts and robust developer logging.
- **Zero-Database Setup**: In-memory and local JSON storage for ultimate portability.

## Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/productlens-ai.git
cd productlens-ai

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Running Locally

To launch the premium Gradio dashboard:
```bash
python app.py
```

To run the CLI pipeline tool:
```bash
python run_demo.py
```

## Hugging Face Spaces Deployment

This application is fully compatible with Hugging Face Spaces (Gradio SDK).

1. Create a new Space on Hugging Face (SDK: Gradio).
2. Upload the project files.
3. In the Space Settings, add your `GEMINI_API_KEY` to the **Repository Secrets**.
4. Hugging Face will automatically install `requirements.txt` and run `app.py`.

## Built With
- **Google Gemini 1.5 Flash** (via `google-generativeai`)
- **Gradio** (Frontend framework)
- **Plotly & Pandas** (Data visualization)
- **Python 3.10+**
