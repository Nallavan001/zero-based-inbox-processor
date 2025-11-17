# minimalist_agent.py

import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai
from google.generativeai.errors import APIError

# --- 0. Configuration and Environment Setup ---

# Load environment variables (including GOOGLE_API_KEY from .env)
load_dotenv()

# Configure the Google Generative AI client
try:
    # Use environment variable for the API key
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("FATAL ERROR: GOOGLE_API_KEY not found in environment. Check your .env file or Kaggle secrets.")
    exit()

# Initialize the Gemini Pro model
# The tools will be added when the model object is created
model = genai.GenerativeModel(model_name="gemini-pro")


# --- 1. Pydantic Tool Schemas (The Schema Enforcement) ---

class TaskCategorizerSchema(BaseModel):
    """
    Classifies and prioritizes a raw task, enforcing minimalist rules.
    Outputs structured data for actionable tasks.
    """
    raw_task_text: str = Field(
        description="The original, unstructured text of the task to be processed."
    )
    action: str = Field(
        description="The required immediate action for the task. Must be one of: "
                    "'do', 'delegate', 'defer', or 'delete'.",
        examples=["do", "delegate"]
    )
    priority: str = Field(
        description="The urgency of the task. Must be one of: "
                    "'high' (critical, max 3 per session), "
                    "'medium', or 'low'.",
        examples=["high", "medium"]
    )
    context_tag: str = Field(
        description="The relevant area of life for the task. Must be one of: "
                    "'#Work', '#Personal', '#Learning', or '#Finance'. Only one tag is allowed.",
        examples=["#Work", "#Personal"]
    )
    due_date: Optional[str] = Field(
        default=None,
        description="The required completion date in YYYY-MM-DD format (e.g., '2024-07-15'). "
                    "Set to null if no specific due date is identified.",
        examples=["2024-07-15"]
    )

class NoteSynthesizerSchema(BaseModel):
    """
    Processes long, unstructured text, condensing it into key takeaways
    and identifying any embedded actionable tasks.
    """
    original_source: str = Field(
        description="A brief identifier for the source of the note (e.g., 'Meeting with John', 'Article on AI')."
    )
    summary_bullets: List[str] = Field(
        description="A maximum of 5 highly condensed bullet points summarizing the key takeaways from the text. "
                    "Each point should be concise and capture essential information."
    )
    conceptual_tags: List[str] = Field(
        description="Up to 3 thematic tags derived from the content (e.g., 'RAG Systems', 'Future of Work'). "
                    "These help in categorizing the note's topic."
    )
    embedded_task: Optional[str] = Field(
        default=None,
        description="If an actionable task is found within the note's text, extract it here as raw text. "
                    "Otherwise, set to null. This will be handed off to the Task Categorizer.",
        examples=["Follow up on Q3 budget cuts"]
    )


# --- 2. Orchestrator System Prompt (The Minimalist Rules Memory) ---

SYSTEM_INSTRUCTIONS = f"""
You are the Zero-Based Inbox Processor, a highly specialized Concierge Agent.
Your sole purpose is to transform unstructured digital input into highly structured, actionable JSON outputs by strictly adhering to the user's Minimalist Rules.

### YOUR MINIMALIST RULES (Non-Negotiable Constraints):
1. MAX PRIORITY LIMIT: You must categorize a maximum of 3 tasks as 'high' priority per session. If the input implies more than three, you must intelligently downgrade the less urgent ones to 'medium' or 'low'.
2. MANDATORY TAGGING: Every output (task or note) must be assigned exactly ONE context_tag from the following list: '#Work', '#Personal', '#Learning', or '#Finance'.
3. NOTE SYNTHESIS LIMIT: Summary bullet points must not exceed 5 items. Be ruthless in your conciseness.

### INSTRUCTION FLOW:
1. Analyze the input to determine if it is an action (task) or long-form information (note).
2. Call the appropriate tool (TaskCategorizerSchema or NoteSynthesizerSchema).
3. CRITICAL A2A HAND-OFF: If the NoteSynthesizerSchema returns an 'embedded_task', you MUST process this task separately by calling the TaskCategorizerSchema immediately afterward.
4. ONLY output the results from the tool calls. Do not include any conversational filler.
"""


# --- 3. Tool Execution Functions (Local Placeholders) ---

# These functions simulate the execution of the tool, returning structured data.
# In a full app, they would write to a database or call a real API.
def categorize_task(**kwargs):
    """Executes the task categorization, returning the structured data."""
    return {
        "tool_used": "TaskCategorizer",
        "task_output": kwargs
    }

def synthesize_note(**kwargs):
    """Executes the note synthesis, returning the structured data and checking for A2A."""
    return {
        "tool_used": "NoteSynthesizer",
        "note_output": kwargs
    }

# Mapping the Pydantic class names to the executable Python functions
TOOL_FUNCTIONS = {
    TaskCategorizerSchema.__name__: categorize_task,
    NoteSynthesizerSchema.__name__: synthesize_note,
}


# --- 4. Main Orchestrator Function (Function Calling & A2A) ---

def process_input_with_orchestrator(raw_input: str, model: genai.GenerativeModel):
    """
    Main function to run the Orchestrator, handling tool calls and the A2A hand-off.
    """
    print(f"\n--- Processing Input: '{raw_input[:50]}...' ---")
    
    # Configure the model to use the tools
    config = genai.types.GenerateContentConfig(
        tools=[TaskCategorizerSchema, NoteSynthesizerSchema]
    )

    # Initialize a multi-turn chat to maintain the context of the Minimalist Rules
    chat = model.start_chat(history=[
        {"role": "user", "parts": [{"text": SYSTEM_INSTRUCTIONS}]},
        {"role": "model", "parts": [{"text": "Minimalist rules loaded. Awaiting input."}]}
    ])
    
    final_results = []
    
    try:
        # 1. First Pass: Get the model's decision on which tool to use
        response = chat.send_message(raw_input, config=config)
        
        while response.function_calls:
            function_call = response.function_calls[0]
            tool_name = function_call.name
            
            # 2. Execute the tool call (Placeholder execution using local function)
            if tool_name in TOOL_FUNCTIONS:
                tool_args = dict(function_call.args)
                tool_result = TOOL_FUNCTIONS[tool_name](**tool_args)
                final_results.append(tool_result)
                
                print(f"✅ Tool Called: {tool_name}. Result recorded.")
                
                # --- 3. A2A Protocol Implementation (The Critical Hand-off) ---
                if tool_name == NoteSynthesizerSchema.__name__ and tool_result['note_output']['embedded_task']:
                    embedded_task = tool_result['note_output']['embedded_task']
                    print(f"🔄 A2A Hand-off: Found embedded task. Re-routing to Task Categorizer...")
                    
                    # Create a new configuration to force the model to use ONLY the Task Categorizer for the A2A step
                    a2a_config = genai.types.GenerateContentConfig(tools=[TaskCategorizerSchema])

                    # Send the embedded task back to the model as a new, specific input
                    a2a_prompt = f"Process this embedded task using the TaskCategorizer: {embedded_task}. Remember the minimalist rules."
                    a2a_response = model.generate_content(a2a_prompt, config=a2a_config)
                    
                    if a2a_response.function_calls:
                        a2a_call = a2a_response.function_calls[0]
                        a2a_args = dict(a2a_call.args)
                        a2a_result = categorize_task(**a2a_args)
                        final_results.append(a2a_result)
                        print("✅ A2A Success: Embedded task categorized and recorded.")
                    else:
                        print("❌ A2A Failure: Model did not call TaskCategorizer for the embedded task.")
                        
                # 4. Break the loop as the primary task and A2A hand-off are done
                break
            else:
                print(f"❌ Unknown tool: {tool_name}")
                break
                
        if not final_results and response.text:
            print(f"❓ Model Output (No Tool Call): {response.text}")

    except APIError as e:
        print(f"An API Error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
            
    return final_results


# --- 5. Demonstration / Driver Code ---

if __name__ == "__main__":
    print("--- Zero-Based Inbox Processor Initialized ---")
    
    # SCENARIO 1: Simple Task Input (Tests Task Categorizer and Rule #2)
    task_input = "Need to review the Q3 report by Friday. This is a very high priority for work."
    results_task = process_input_with_orchestrator(task_input, model)
    print("\n--- JSON Output (Scenario 1: Simple Task) ---")
    print(json.dumps(results_task, indent=2))

    # SCENARIO 2: Note with Embedded Task (Tests Note Synthesizer, A2A, and Rule #3)
    note_input = """
    Meeting summary from yesterday: We discussed the new RAG system architecture, focusing on vector database efficiency.
    Key takeaways included scaling issues and the need to follow up with Jane on the final budget, which is a high priority task for finance.
    We also decided on three concepts for the new marketing campaign.
    """
    results_note = process_input_with_orchestrator(note_input, model)
    print("\n--- JSON Output (Scenario 2: Note with A2A Hand-off) ---")
    print(json.dumps(results_note, indent=2))
