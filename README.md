Here is the fully updated README.md with the Live Demo link added prominently at the top.

Markdown

# 🚀 AI-Powered HARO Response Agent (Scholar Edition)

> **Automate your PR pitches with high-authority research, academic backing, and strategic writing.**

This tool is not just a text generator. It is an **Agentic AI Workflow** designed to solve the "Help A Reporter Out" (HARO) challenge. It autonomously researches the journalist's query using live web data and Google Scholar, formulates a winning strategy, and drafts a human-like pitch that adheres to strict negative constraints to bypass spam filters.

### 🔴 [Live Demo: Try the App Here](https://haro-response-agent.onrender.com)

---

## 🧠 Core Architecture

The system orchestrates three specialized AI Agents to mimic a human PR team:

### 1. ♟️ The Strategist Agent
* **Role:** The "Brain."
* **Function:** Analyzes the journalist's query against your specific user profile.
* **Output:** Determines the optimal **Tone** (e.g., Authoritative, Contrarian) and **Angle** before any writing begins.

### 2. 🕵️ The Researcher Agent (The Heavy Lifter)
* **Role:** The "Fact-Checker."
* **Capabilities:**
    * **High-DR Filtering:** Searches only high-authority domains (`.gov`, `.edu`, `forbes.com`, etc.) using SerpApi.
    * **Academic Deep Dive:** Queries **Google Scholar** for relevant papers published in recent years.
    * **Fallback Logic:** If Scholar yields no results, it automatically falls back to the **CORE API** (Open Access repository).
    * **Smart Scraping:** Uses `trafilatura` to extract clean text from URLs and `PyMuPDF` to parse PDF research papers on the fly.

### 3. ✍️ The Writer Agent
* **Role:** The "Copywriter."
* **Function:** Synthesizes the strategy and research into a pitch.
* **Guardrails:** Implements **Strict Negative Constraints**:
    * *No location names* (prevents hallucinating local context).
    * *No robotic phrasing* (e.g., "Here in...").
    * *Anti-Echo* (prevents repeating the question).
    * *British English enforcement.*

---

## 🛠️ Tech Stack

* **Core:** Python 3.9+, Flask
* **LLM Integration:** OpenAI API (GPT-4o-mini) / Google Gemini (Optional support)
* **Search & Data:** SerpApi (Google Search & Scholar), CORE API
* **Scraping & Parsing:** `trafilatura`, `PyMuPDF` (fitz)

---

## 🚀 Getting Started

### Prerequisites

You will need API keys for the following services:
1.  **OpenAI API Key** (for reasoning and writing)
2.  **SerpApi Key** (for Google Search and Scholar results)
3.  **CORE API Key** (Optional, for academic fallback)

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/haro-agent.git](https://github.com/yourusername/haro-agent.git)
    cd haro-agent
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application Locally

1.  Start the Flask server:
    ```bash
    python app.py
    ```
    *Note: The app runs on `http://0.0.0.0:5000` by default.*

2.  Open your browser and navigate to:
    `http://localhost:5000`

---

## 🖥️ Usage Guide

1.  **API Keys:** Enter your OpenAI and SerpApi keys in the dashboard.
2.  **Expert Profile:** Paste your professional bio (e.g., "Senior Fintech CEO with 15 years in High-Frequency Trading").
3.  **Context:**
    * **Target Market:** e.g., "Sweden" (The AI uses this for context but is forbidden from naming it).
    * **Start Year:** Filter research papers published after this year.
4.  **Query:** Paste the full HARO/Connectively query from the journalist.
5.  **Generate:** Click the button and watch the agents work.

---

## 📂 Project Structure

```text
haro-agent/
│
├── agents/
│   ├── __init__.py
│   ├── strategist.py    # Analyzes query for Tone/Angle
│   ├── researcher.py    # Handles SerpApi, Scholar, CORE, and Scraping
│   └── writer.py        # GPT-4o Writer with strict constraints
│
├── templates/
│   └── index.html       # Frontend UI with logs and inputs
│
├── app.py               # Main Flask application entry point
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
🛡️ Robustness & Error Handling
PDF Parsing: If a PDF is found but cannot be downloaded (paywall/timeout), the system gracefully logs the failure but still captures the citation link for the writer.

Search Fallbacks: If the primary academic search (Scholar) returns zero results, the system seamlessly triggers a secondary search on the CORE database.

Content Extraction: Uses trafilatura to ignore website navigation/ads and extract only the main article body for the LLM to read.

🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements, specifically in adding new research sources or refining the agent prompts.

Built with ❤️ during my internship.