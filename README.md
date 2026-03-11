# Simple Multi-Agent System Example

A beginner-friendly Python example that shows how to build a small multi-agent system with local language models.

This repository includes one main file:

- `simple_llama_agent.py`

The example demonstrates a practical multi-agent design where a main Llama-based agent can answer general questions, use tools, remember recent conversation, and delegate technical questions to a specialist Mistral-based agent.

## What is a multi-agent system?

A multi-agent system is an application where more than one agent has a role in solving user requests. Instead of using a single model for everything, you split responsibilities.

In this example:

- **Main Agent** handles general conversation
- **Tool Layer** handles deterministic tasks like time and math
- **Specialist Agent** handles technical or coding questions
- **Memory** keeps recent context across turns
- **Decision Logic** routes each request to the best path

## Architecture used in this example

This script demonstrates five core parts of a simple multi-agent system:

1. **Model loading**
   - Tries to load `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
   - Falls back to `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`

2. **Memory**
   - Stores recent user and agent messages
   - Reuses that context in later prompts

3. **Tools**
   - Time tool
   - Basic calculator tool

4. **Agent delegation**
   - Loads a Mistral model on demand
   - Sends technical questions to the specialist agent

5. **Decision logic**
   - Decides whether to use a tool, use the main model, or delegate to another agent

## How to create a simple multi-agent system

A simple pattern is:

### 1. Start with one main orchestrator agent
Create a main agent that receives user input and decides what to do next.

### 2. Add short-term memory
Store recent conversation turns so the system can answer follow-up questions with context.

### 3. Add tools for deterministic tasks
Use direct functions for tasks like:

- time and date
- math
- file lookups
- API calls

Tools are faster and more reliable than asking a model for these operations.

### 4. Add specialist agents
Create another agent for a narrower task, such as:

- coding help
- database queries
- policy analysis
- planning
- domain-specific reasoning

### 5. Add routing logic
Use simple rules first. For example:

- if user asks for time → use time tool
- if user asks for math → use calculator
- if user asks for technical explanation → delegate to specialist agent
- otherwise → use main model

### 6. Keep each agent role clear
Good multi-agent systems work best when each agent has a clear responsibility.

### 7. Improve step by step
Once the simple version works, you can add:

- better routing
- structured messages between agents
- logging and tracing
- shared memory
- safety checks
- evaluation metrics

## Requirements

- Python 3
- `llama-cpp-python`
- Local GGUF model files in `~/models/`

Expected model files:

- `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf` or `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`
- `Mistral-7B-Instruct-v0.3.Q4_K_M.gguf`

Install dependency:

```bash
pip install llama-cpp-python
```

## Run

```bash
python3 simple_llama_agent.py
```

## Example prompts

- `What time is it?`
- `Calculate 25*4`
- `Explain Python classes`
- `Analyze this algorithm`
- `What is the capital of Japan?`

## What happens during execution

- The main agent loads first
- The specialist Mistral agent loads only when needed
- User input is routed by simple decision logic
- Tool calls are used for time and math
- Technical questions are delegated to the specialist agent
- Recent conversation is stored and reused

## Why this example is useful

This repository is a good starting point if you want to learn:

- local agent design
- multi-agent routing
- specialist-agent delegation
- tool-augmented agents
- memory-aware prompting

It keeps the implementation small while still showing the main building blocks of a real multi-agent workflow.
