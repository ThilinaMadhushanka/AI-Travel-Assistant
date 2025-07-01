import os
import time
import requests
from dotenv import load_dotenv
from utils.retry import get_retry_delay

def run_booking_huggingface(input_text):
    """Using Hugging Face Inference API (Free)"""
    load_dotenv()
    
    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    prompt = f"""As a Travel Booking Specialist, suggest the best travel options for the following itinerary and budget:
    {input_text}
    
    Please provide:
    1. Recommended flights with estimated prices
    2. Suggested accommodations with price ranges
    3. Booking tips and best practices
    4. Alternative options for different price points
    5. Links to popular booking platforms
    6. Seasonal considerations and best booking times

    Format the response in a clear, organized manner with specific recommendations."""

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
                return f"Error generating booking suggestions: {str(e)}"

def run_booking_gemini(input_text):
    """Using Google Gemini (Free tier)"""
    load_dotenv()
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""As a Travel Booking Specialist, suggest the best travel options for the following itinerary and budget:
        {input_text}
        
        Please provide:
        1. Recommended flights with estimated prices
        2. Suggested accommodations with price ranges
        3. Booking tips and best practices
        4. Alternative options for different price points
        5. Links to popular booking platforms
        6. Seasonal considerations and best booking times

        Format the response in a clear, organized manner with specific recommendations."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error with Gemini API: {str(e)}"

def run_booking_groq(input_text):
    """Using Groq (Free tier)"""
    load_dotenv()
    
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = f"""As a Travel Booking Specialist, suggest the best travel options for the following itinerary and budget:
        {input_text}
        
        Please provide:
        1. Recommended flights with estimated prices
        2. Suggested accommodations with price ranges
        3. Booking tips and best practices
        4. Alternative options for different price points
        5. Links to popular booking platforms
        6. Seasonal considerations and best booking times

        Format the response in a clear, organized manner with specific recommendations."""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error with Groq API: {str(e)}"

def run_booking(input_text):
    """Try multiple free APIs in order of preference"""
    
    # Try Groq first (fastest and most reliable free API)
    if os.getenv("GROQ_API_KEY"):
        result = run_booking_groq(input_text)
        if not result.startswith("Error"):
            return result
    
    # Try Gemini second
    if os.getenv("GEMINI_API_KEY"):
        result = run_booking_gemini(input_text)
        if not result.startswith("Error"):
            return result
    
    # Try Hugging Face as fallback
    if os.getenv("HUGGINGFACE_API_KEY"):
        result = run_booking_huggingface(input_text)
        if not result.startswith("Error"):
            return result
    
    return "Error: No valid API keys found. Please set GROQ_API_KEY, GEMINI_API_KEY, or HUGGINGFACE_API_KEY in your .env file."