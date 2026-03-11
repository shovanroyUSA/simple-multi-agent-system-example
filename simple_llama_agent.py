#!/usr/bin/env python3
"""
Simple Multi-Agent System Example
Demonstrates 5-part agent architecture: Model + Memory + Tools + Decision + Agent Delegation
Uses TinyLlama-1.1B-Chat or Llama-3.1-8B-Instruct model

This Llama Agent can delegate tasks to the Simple Agent (Mistral model) when needed.
"""

from llama_cpp import Llama
from pathlib import Path
from datetime import datetime
import re
import time

# ============================================================================
# PART 1: MODEL LOADING - Initialize Llama LLM
# ============================================================================

# Try Llama-3.1-8B first, fallback to TinyLlama if not available
MODEL_CANDIDATES = [
    ("Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf", "Llama-3.1-8B (4.6GB)", 2048),
    ("tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", "TinyLlama-1.1B (lightweight)", 2048),
]

MODEL_PATH = None
MODEL_NAME = None
CONTEXT_SIZE = None

for candidate, display_name, ctx_size in MODEL_CANDIDATES:
    path = Path.home() / "models" / candidate
    if path.exists():
        MODEL_PATH = path
        MODEL_NAME = display_name
        CONTEXT_SIZE = ctx_size
        break

if not MODEL_PATH:
    print("ERROR: No compatible model found in ~/models/")
    print(f"Looking for: {', '.join([c[0] for c in MODEL_CANDIDATES])}")
    exit(1)

print("=" * 70)
print("LLAMA MULTI-AGENT SYSTEM STARTUP")
print("=" * 70)
print(f"Main Agent: {MODEL_NAME}")
print(f"Context window: {CONTEXT_SIZE} tokens")
print("Architecture: 5-Part Agent System")
print("  1. MODEL - Llama LLM for general tasks")
print("  2. MEMORY - Conversation history tracking")
print("  3. TOOLS - Time and Calculator utilities")
print("  4. AGENT DELEGATION - Can call Simple Agent (Mistral)")
print("  5. DECISION LOGIC - Smart routing system")
print("=" * 70)

# Try to load model, fallback if it fails
model = None
loaded_model_name = None

for candidate, display_name, ctx_size in MODEL_CANDIDATES:
    path = Path.home() / "models" / candidate
    if path.exists():
        try:
            print(f"Attempting to load {display_name}...", end=" ")
            model = Llama(
                model_path=str(path),
                n_ctx=ctx_size,
                n_threads=4,
                n_gpu_layers=0,
                verbose=False
            )
            loaded_model_name = display_name
            print("✓ Loaded successfully")
            break
        except Exception as e:
            print(f"✗ Failed ({str(e)[:30]}...)")
            continue

if not model:
    print("ERROR: Could not load any model")
    exit(1)

print("✓ Main Agent ready")
print("  Simple Agent (Mistral) will load on-demand when needed")
print("=" * 70)

# ============================================================================
# PART 2: MEMORY - Conversation history (list of messages)
# ============================================================================

memory = []  # List of (role, text) tuples - "user" or "assistant"
MAX_MEMORY_TURNS = 6  # Keep last 6 conversation turns


def add_to_memory(role, text):
    """Add message to memory and maintain max size"""
    memory.append((role, text))
    # Keep only last MAX_MEMORY_TURNS interactions
    if len(memory) > MAX_MEMORY_TURNS * 2:
        memory.pop(0)


def format_memory_for_context():
    """Format memory into a context string for the model"""
    if not memory:
        return ""
    
    context = "Previous conversation:\n"
    for role, text in memory[-6:]:  # Show last 6 messages
        if role == "user":
            context += f"User: {text}\n"
        else:
            context += f"Agent: {text}\n"
    return context


# ============================================================================
# PART 3: TOOLS - Functions the agent can call
# ============================================================================

def tool_get_time():
    """Tool: Get current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def tool_calculate(expression):
    """Tool: Safe calculator (basic math only)"""
    try:
        # Only allow safe math operations
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "ERROR: Invalid characters in expression"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


# ============================================================================
# PART 4: AGENT DELEGATION - Call another specialized agent
# ============================================================================

# Load the Simple Agent (Mistral model) as a specialist
simple_agent_model = None
SIMPLE_AGENT_AVAILABLE = False

def load_simple_agent():
    """Load the Simple Agent (Mistral specialist) on-demand"""
    global simple_agent_model, SIMPLE_AGENT_AVAILABLE
    
    if simple_agent_model is not None:
        return True
    
    try:
        mistral_path = Path.home() / "models" / "Mistral-7B-Instruct-v0.3.Q4_K_M.gguf"
        if not mistral_path.exists():
            print("  [Simple Agent unavailable: Mistral model not found]")
            return False
        
        print("  [Loading Simple Agent (Mistral specialist)...]", end=" ")
        simple_agent_model = Llama(
            model_path=str(mistral_path),
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False
        )
        SIMPLE_AGENT_AVAILABLE = True
        print("✓ Ready")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def delegate_to_simple_agent(user_input):
    """
    Delegate a complex question to the Simple Agent (Mistral specialist)
    This demonstrates multi-agent communication!
    """
    if not SIMPLE_AGENT_AVAILABLE:
        if not load_simple_agent():
            return "Simple Agent unavailable. Using main agent instead."
    
    # Create prompt for the specialist agent
    prompt = f"""You are a technical specialist agent. Provide specific technical answers.

Question: {user_input}
Answer:"""
    
    # Ask the Simple Agent
    response = simple_agent_model(
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
        top_p=0.95,
        #stop=["Question:", "question:"]
        stop=["\n\nQuestion:", "\n\nUser:"]
    )
    
    return response["choices"][0]["text"].strip()


# ============================================================================
# PART 5: DECISION LOGIC - Route user input to tool, model, or another agent
# ============================================================================

def decide_action(user_input):
    """Decide whether to use a tool, ask the model, or delegate to another agent"""
    
    # Check for time-related keywords
    if any(word in user_input.lower() for word in ["time", "date", "clock", "what time", "current time"]):
        return "tool_time"
    
    # Check for math-related keywords
    if any(word in user_input.lower() for word in ["calculate", "compute", "math", "how much", "what is"]) and any(c in user_input for c in "+-*/("):
        return "tool_math"
    
    # Check if we should delegate to Simple Agent (Mistral specialist)
    # Delegate for: technical questions, coding, detailed analysis
    if any(word in user_input.lower() for word in ["code", "python", "programming", "algorithm", "technical", "explain in detail", "analyze"]):
        return "delegate_agent"
    
    # Default to model inference
    return "model"


def execute_tool(tool_name, user_input=None):
    """Execute selected tool"""
    if tool_name == "tool_time":
        return tool_get_time()
    elif tool_name == "tool_math":
        # Extract expression from user input
        numbers_match = re.search(r'[\d\s+\-*/().]+', user_input)
        if numbers_match:
            expression = numbers_match.group(0).strip()
            return tool_calculate(expression)
        return "Could not parse math expression"
    return "Unknown tool"


def ask_model(user_input):
    """Ask the model to generate a response"""
    
    # Build context with memory
    memory_context = format_memory_for_context()
    
    # Create prompt with Llama-3 chat format
    prompt = f"""You are a helpful AI agent. Be concise and friendly.

{memory_context}

User: {user_input}
Agent:"""
    
    # Generate response
    response = model(
        prompt=prompt,
        max_tokens=256,
        temperature=0.7,
        top_p=0.95,
        stop=["User:", "user:"]
    )
    
    # Extract text from response
    generated_text = response["choices"][0]["text"].strip()
    return generated_text


# ============================================================================
# MAIN LOOP - Agent interaction loop
# ============================================================================

def main():
    print("\n📝 Multi-Agent System Ready! Type 'quit' to exit")
    print("=" * 70)
    print("CAPABILITIES:")
    print("  • Time Tool: 'What time is it?'")
    print("  • Calculator Tool: 'Calculate 25*4'")
    print("  • Main Agent (Llama): General questions")
    print("  • Simple Agent (Mistral): 'Explain Python code' or technical questions")
    print("=" * 70)
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("Agent: Goodbye! 👋")
                break
            
            # Add user input to memory
            add_to_memory("user", user_input)
            print(f"[Memory: {len(memory)//2} turns stored]")
            
            # Decide action
            action = decide_action(user_input)
            print(f"[Decision: {action}]")
            
            # Execute action
            if action == "model":
                print("Agent: ", end="", flush=True)
                start_time = time.time()
                response = ask_model(user_input)
                elapsed = time.time() - start_time
                print(response)
                print(f"[Generated in {elapsed:.2f}s by Main Agent]")
            elif action == "delegate_agent":
                print("Agent: [Delegating to Simple Agent specialist...]")
                start_time = time.time()
                response = delegate_to_simple_agent(user_input)
                elapsed = time.time() - start_time
                print(f"Agent: {response}")
                print(f"[Generated in {elapsed:.2f}s by Simple Agent]")
            else:
                response = execute_tool(action, user_input)
                print(f"Agent: {response}")
            
            # Add response to memory
            add_to_memory("assistant", response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nAgent: Interrupted by user")
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
