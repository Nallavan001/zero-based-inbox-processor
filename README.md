# 🤖 The Zero-Based Inbox Processor: Schema-Enforced Productivity through Task & Note Synthesis

**Capstone Project for the AI Agents Intensive Course (Concierge Agents Track)**

## 🎯 Problem Statement

The modern digital landscape imposes **digital decision fatigue**—the strain of constantly sorting and prioritizing scattered, unstructured inputs. We address the need for a system that doesn't just suggest organization, but *enforces* a rigorous, constrained structure.

## 🌟 The Solution: Zero-Based Processing

The **Zero-Based Inbox Processor** is a specialized Concierge Agent that enforces strict **Minimalist Rules** on all inputs. It transforms digital chaos into a single, highly structured, and actionable JSON output, eliminating manual decision-making and cognitive load.

## 🏛️ Architecture and Key Features

This agent implements a multi-tool architecture leveraging advanced AI capabilities:

1.  **Orchestrator Agent (The Minimalist):** Manages the workflow and enforces the **Minimalist Rules** (e.g., Max 3 High Priority Tasks) embedded in its system prompt (Long-Term Memory).
2.  **Schema Enforcement (Function Calling):** Uses Pydantic to strictly enforce structured output via two specialized tools:
    * `TaskCategorizerSchema`
    * `NoteSynthesizerSchema`
3.  **Agent-to-Agent (A2A) Protocol:** When the `NoteSynthesizer` extracts an `embedded_task` from long text, the Orchestrator executes a crucial A2A hand-off, passing the raw task to the `TaskCategorizer` for immediate, dedicated prioritization.
4.  **Sessions & Memory:** A new session is started for each processing run to maintain context and enforce session-specific limits.

## 🛠️ Setup and Installation

### Prerequisites

* Python 3.9+
* A Google AI API Key (Set up as an environment variable)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Nallavan001/zero-based-inbox-processor/
    cd minimalist-mastery-agent
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # .\venv\Scripts\activate.bat # On Windows
    pip install -r requirements.txt
    ```

3.  **Set your API Key:**
    * Create a file named `.env` in the root directory.
    * Add your API key: `GOOGLE_API_KEY=YOUR_API_KEY_HERE`

4.  **Run the demo:**
    ```bash
    python minimalist_agent.py
    ```

## 📸 Demonstration

*(**IMPORTANT:** Replace the conceptual images/JSON output below with your actual screenshots and JSON output from a successful run of `minimalist_agent.py`.)*

### Scenario 1: Processing a Simple Task

*(Insert your "Before" image representing a typical task or email here)*
> **Input:** An email or note containing a single, clear task.

**Output (JSON):** The agent correctly categorizes and prioritizes the task according to the defined schema and minimalist rules.

```json
{
  "tool_used": "TaskCategorizer",
  "task_output": {
    "raw_task_text": "Need to review the Q3 report by Friday. This is a very high priority for work.",
    "action": "do",
    "priority": "high",
    "context_tag": "#Work",
    "due_date": "2025-07-19"
  }
}
```

Scenario 2: Note with Embedded Task (A2A Protocol in Action)
<img width="1024" height="1024" alt="Gemini_Generated_Image_ommvoyommvoyommv (1)" src="https://github.com/user-attachments/assets/d9887be6-44fe-4e4f-b459-f534d9ee3cb8" />

Input: A long, unstructured meeting summary text containing an embedded task.

Output (JSON): The agent first synthesizes the note, then performs an A2A hand-off to categorize the embedded task, demonstrating a multi-step intelligent workflow.

```json
[
  {
    "tool_used": "NoteSynthesizer",
    "note_output": {
      "original_source": "Meeting summary from yesterday",
      "summary_bullets": [
        "Discussed new RAG system architecture.",
        "Focused on vector database efficiency.",
        "Identified scaling issues.",
        "Decided on three concepts for new marketing campaign."
      ],
      "conceptual_tags": [
        "RAG Systems",
        "AI",
        "Marketing"
      ],
      "embedded_task": "follow up with Jane on the final budget, which is a high priority task for finance"
    }
  },
  {
    "tool_used": "TaskCategorizer",
    "task_output": {
      "raw_task_text": "follow up with Jane on the final budget, which is a high priority task for finance",
      "action": "do",
      "priority": "high",
      "context_tag": "#Finance",
      "due_date": null
    }
  }
]
```

🔗 Project Card / Thumbnail
<img width="1024" height="1024" alt="Gemini_Generated_Image_2apoat2apoat2apo" src="https://github.com/user-attachments/assets/9f8daf2b-4407-48ba-9b70-5e814b5645a2" />
