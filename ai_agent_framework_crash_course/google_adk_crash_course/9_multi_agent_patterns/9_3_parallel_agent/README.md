# ⚡ Tutorial 9.3: Parallel Agents - Market Snapshot Team

## 🎯 What You'll Learn

- **Parallel Agent Composition**: How to orchestrate multiple specialized agents concurrently
- **Shared State**: How parallel children write to a common `session.state` safely
- **Branching Context**: Invocation branches for clean, isolated tool/memory context
- **Streamlit Interface**: A simple UI to run and visualize parallel results

## 🧠 Core Concept: ParallelAgent with Shared State

According to the ADK docs, **Parallel Agents** execute their sub-agents concurrently. Each child runs on its own invocation branch but shares the same `session.state`.

```
Topic → ParallelAgent → 3 Sub-agents (Concurrent Execution)
             ↓
   [Market Trends] + [Competitors] + [Funding News]
             ↓
            Snapshot in state
```

Each child agent writes results to a distinct key in shared state to avoid overwrites: `market_trends`, `competitors`, `funding_news`.

## 📁 Project Structure

```
9_3_parallel agent/
├── agent.py              # Parallel workflow (3 research agents + ParallelAgent)
├── app.py                # Streamlit UI to run and view snapshot
├── requirements.txt      # Python dependencies
├── README.md             # This documentation
└── .env.example          # Example environment variables
```

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd "9_3_parallel agent"
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file with your Google API key:
```bash
echo "GOOGLE_API_KEY=your_ai_studio_key_here" > .env
```

> Get your key from Google AI Studio.

### 3. Run the Streamlit App
```bash
streamlit run app.py
```

## 🧪 How It Works

- `ParallelAgent` executes `market_trends_agent`, `competitor_intel_agent`, and `funding_news_agent` concurrently.
- Each child uses web search and writes to a unique `output_key` in `session.state`.
- The UI reads `session.state` and displays a 3-column snapshot.

## 🔧 ADK Concepts Demonstrated

- ParallelAgent pattern and event interleaving
- Shared `session.state` with distinct keys per child
- Invocation branches for contextual separation
- Runner + Session services for execution

## 📚 Key Takeaways

- Parallel fan-out is ideal for independent data gathering
- Keep output keys distinct to avoid overwrites in shared state
- Combine with a downstream synthesizer agent if you need a single report

