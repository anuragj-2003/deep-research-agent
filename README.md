# DeepResearcher: Autonomous Research Agent 🚀

**DeepResearcher** is a powerful, autonomous AI agent designed to perform deep web research, synthesize findings, and generate professional reports in multiple formats. Built with **LangGraph**, **LangChain**, and **Llama 3**, it features an intelligent state-machine workflow that handles the entire research lifecycle—from understanding your intent to delivering the final product via email.

## Key Features ✨

*   **🧠 Smart Intent Parsing**: Just say *"Research Quantum Computing and send a pdf to me@example.com"*. The agent intelligently extracts the topic, desired format, and email address.
*   **🌐 Autonomous Web Research**: Orchestrates a ReAct loop using **Tavily Search** and **Web Scraping** tools to gather comprehensive information.
*   **📚 RAG Framework**: Indices all research findings into a local **FAISS Vector Store**, ensuring reports are grounded in retrieved context (Retrieval-Augmented Generation).
*   **📝 Multi-Format Reporting**: Generates high-quality reports in **PDF**, **PPTX** (PowerPoint), **DOCX**, and **Markdown**.
*   **📧 Automated Delivery**: creating and sending emails with the report attached automatically.
*   **🔄 Interactive Follow-up loop**: Supports a continuous research loop. Ask follow-up questions like *"Now generate a ppt for this"* and the agent adapts without losing context.
*   **💾 State Persistence**: Built on LangGraph with Checkpointing to maintain state across interactions.

## Architecture 🏗️

The agent is modeled as a state graph with the following nodes:
1.  **Parse Input**: Extracts intent from natural language.
2.  **Research**: Executes search/scrape tools and updates the Knowledge Base (Vector Store).
3.  **Summarize**: Synthesizes findings.
4.  **Report**: Generates the document using RAG.
5.  **Email**: Dispatches the report.
6.  **Follow-up**: Handles user feedback and loops back if needed.

## Setup 🛠️

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/yourusername/deep-research-agent.git
    cd deep-research-agent
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file with your keys:
    ```bash
    GROQ_API_KEY=gsk_...
    TAVILY_API_KEY=tvly-...
    SMTP_USER=your_email@gmail.com
    SMTP_PASSWORD=your_app_password
    ```

4.  **Run**:
    ```bash
    python main.py
    ```

## Tech Stack 💻
*   **Python 3.10+**
*   **LangGraph** (Orchestration)
*   **LangChain** (Framework)
*   **Groq API** (Llama 3.1 Inference)
*   **FAISS** (Vector Database)
*   **Tavily** (Search Engine)
