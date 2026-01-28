# Simple Software Bug Assistant

This is a simplified version of the Software Bug Assistant using Google's Agent Development Kit (ADK).
It uses a local Python script with a simple Date tool and a DuckDuckGo search tool.


## Prerequisites

- **Python 3.10+** (REQUIRED - The `google-adk` library does not support Python 3.8 or 3.9)
- A Google Cloud Project with Vertex AI API enabled (if using Vertex AI) OR a Google AI Studio API Key.

## Installation

1.  **Clone or download** this project to your local machine.
2.  **Install the dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## Setup Credentials

You need to provide credentials for the Gemini model.

**Option A: Google AI Studio API Key (Easiest for local dev)**
Create a `.env` file (or export in your terminal) with your key:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Option B: Vertex AI**
If you have the Google Cloud CLI installed:

```bash
gcloud auth login
gcloud auth application-default login
```

## Running the Agent

Run the agent script:

```bash
python simple_agent.py
```

## Usage

Once running, you can type natural language queries.
Examples:
- "What is today's date?"
- "Search for the latest version of Python."
- "What are the common bugs in the requests library?"
