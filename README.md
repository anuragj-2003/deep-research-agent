# Deep Research Agent 🚀

An autonomous AI agent built with **LangGraph** that performs deep web research, synthesizes professional reports, and delivers them via email as `.docx` attachments.

## Features
- **Deep Web Search**: Leverages Tavily for comprehensive information retrieval.
- **Iterative Planning**: Uses a planner node to break down complex queries into sub-tasks.
- **Premium Report Generation**: Dynamically generates a high-quality Markdown report based on research.
- **DOCX Export**: Automatically converts research results into a structured Microsoft Word document.
- **Email Delivery**: Sends the report as an attachment via Gmail SMTP.
- **Human-In-The-Loop**: Pauses execution to ask the user for the receiver's email address using `interrupt()`.
- **Flexible LLM Support**: Designed to work with Groq (Llama 3) or Gemini.

## Prerequisites
- Python 3.9+
- [LangGraph CLI](https://github.com/langchain-ai/langgraph)
- API Keys:
  - [Groq API Key](https://wow.groq.com/)
  - [Tavily API Key](https://tavily.com/)
- [Gmail App Password](https://support.google.com/accounts/answer/185833) (for SMTP)

## Setup

1. **Clone and Install**:
```bash
git clone <your-repo-url>
cd deep_research_agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Environment Variables**:
Create a `.env` file in the root:
```env
GROQ_API_KEY="your_groq_key"
TAVILY_API_KEY="your_tavily_key"
GROQ_MODEL="llama-3.3-70b-versatile"

# SMTP
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
```

3. **Run Locally**:
```bash
langgraph dev
```

## Deployment

This agent is optimized for **LangGraph Cloud (LangSmith)**.
1. Push this repository to GitHub.
2. In LangSmith, create a **New Deployment**.
3. Mirror your `.env` variables into the LangSmith deployment settings.
4. Access your agent via the cloud-hosted Studio or API!
