# filepath: f:\AI project\Agent AI\app.py
import streamlit as st
from workflows.trip_graph import plan_trip
import os
from dotenv import load_dotenv
from openai import OpenAI
from crewai import Crew
from litellm import RateLimitError, AuthenticationError
import time

# Load environment variables
load_dotenv()

# Configure CrewAI
api_key = os.getenv("OPENAI_API_KEY")

def validate_api_key(key):
    if not key:
        return False, "OpenAI API key not found in .env file"
    if not key.startswith('sk-'):
        return False, "Invalid API key format. Should start with 'sk-'"
    if len(key) < 50:  # OpenAI API keys are typically longer
        return False, "API key appears to be too short"
    return True, None

# Validate API key
is_valid, error_message = validate_api_key(api_key)
if not is_valid:
    st.error(f"API Key Validation Error: {error_message}")
    st.error("Please update your API key in the .env file")
    st.stop()

# Initialize OpenAI
try:
    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")
    st.stop()

st.title("Multimodal Travel Assistant")

input_text = st.text_input("Where do you want to go and what's your budget?")

if st.button("Plan Trip"):
    try:
        time.sleep(1)  # Adds a 1 second delay between requests
        result = plan_trip({"input": input_text})
        st.write(result)
    except AuthenticationError:
        st.error("Authentication failed. Please check your OpenAI API key.")
    except RateLimitError:
        st.error("API rate limit exceeded. Please check your OpenAI API key quota and billing status.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")