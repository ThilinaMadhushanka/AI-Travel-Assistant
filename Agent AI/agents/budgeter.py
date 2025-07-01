import os
import time
import requests
from dotenv import load_dotenv
from utils.retry import get_retry_delay

def run_budgeter_huggingface(input_text):
    """Using Hugging Face Inference API (Free)"""
    load_dotenv()
    
    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    prompt = f"""As a Financial Advisor specializing in travel, create a detailed budget breakdown for the following itinerary:
    {input_text}
    
    Please provide:
    1. Transportation costs (flights, local transport)
    2. Accommodation costs
    3. Food and dining expenses
    4. Activity and attraction costs
    5. Additional expenses (visas, insurance, etc.)
    6. Total estimated budget
    7. Money-saving tips

    Format the response in a clear, organized manner with estimated costs."""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 1000,
            "temperature": 0.7,
            "do_sample": True
        }
    }

    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', 'No response generated')
                return str(result)
            elif response.status_code == 503:
                time.sleep(20)  # Model is loading
                continue
            else:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        except Exception as e:
            if attempt < 2:
                time.sleep(get_retry_delay(attempt))
            else:
                return f"Error generating budget: {str(e)}"

def run_budgeter_gemini(input_text):
    """Using Google Gemini (Free tier)"""
    load_dotenv()
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""As a Financial Advisor specializing in travel, create a detailed budget breakdown for the following itinerary:
        {input_text}
        
        Please provide:
        1. Transportation costs (flights, local transport)
        2. Accommodation costs
        3. Food and dining expenses
        4. Activity and attraction costs
        5. Additional expenses (visas, insurance, etc.)
        6. Total estimated budget
        7. Money-saving tips

        Format the response in a clear, organized manner with estimated costs."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error with Gemini API: {str(e)}"

def run_budgeter_groq(input_text):
    """Using Groq (Free tier)"""
    load_dotenv()
    
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = f"""As a Financial Advisor specializing in travel, create a detailed budget breakdown for the following itinerary:
        {input_text}
        
        Please provide:
        1. Transportation costs (flights, local transport)
        2. Accommodation costs
        3. Food and dining expenses
        4. Activity and attraction costs
        5. Additional expenses (visas, insurance, etc.)
        6. Total estimated budget
        7. Money-saving tips

        Format the response in a clear, organized manner with estimated costs."""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error with Groq API: {str(e)}"

def run_budgeter(input_text):
    """Try multiple free APIs in order of preference"""
    
    # Try Groq first
    if os.getenv("GROQ_API_KEY"):
        result = run_budgeter_groq(input_text)
        if not result.startswith("Error"):
            return result
    
    # Try Gemini 
    if os.getenv("GEMINI_API_KEY"):
        result = run_budgeter_gemini(input_text)
        if not result.startswith("Error"):
            return result
    
    # Try Hugging
    if os.getenv("HUGGINGFACE_API_KEY"):
        result = run_budgeter_huggingface(input_text)
        if not result.startswith("Error"):
            return result
    
    return "Error: No valid API keys found. Please set GROQ_API_KEY, GEMINI_API_KEY, or HUGGINGFACE_API_KEY in your .env file."