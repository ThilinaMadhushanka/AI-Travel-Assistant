# AI Travel Assistant

An intelligent travel planning application that uses AI to help users plan their trips, manage budgets, and find the best travel deals.

## Features

- 🌍 Intelligent trip planning with day-by-day itineraries
- 💰 Smart budget management and cost optimization
- 🏨 Automated booking suggestions for flights and hotels
- 🎯 Multi-agent system using CrewAI
- 🔄 Sequential workflow processing
- 🖼️ Support for multimodal inputs (text, images, audio)

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection

## Installation

1. Clone the repository:
```bash
git clone <my-repository-url>
cd Agent-AI
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```properties
OPENAI_API_KEY=my_api_key_here
CREWAI_MODEL=llama2
LOCAL_AI_URL=http://localhost:8000
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Enter your destination and budget in the text input field
3. Click "Plan Trip" to generate your personalized travel plan

## Project Structure

```
Agent-AI/
├── agents/
│   ├── planner.py
│   ├── budgeter.py
│   └── booking.py
├── utils/
│   ├── api_wrappers.py
│   ├── memory.py
│   └── multimodal_input.py
├── workflows/
│   └── trip_graph.py
├── app.py
├── requirements.txt
└── .env
```


## Acknowledgments

- OpenAI for their API
- CrewAI framework
- LangGraph for workflow management
- Streamlit for the web interface
