import os
from dotenv import load_dotenv

def transcribe_audio_free(audio_file_path):
    """
    Free audio transcription using OpenAI Whisper (runs locally)
    No API key required!
    """
    try:
        import whisper
        
        # Load the model
        model = whisper.load_model("base")  
        
        # Transcribe the audio
        result = model.transcribe(audio_file_path)
        return result['text']
    except ImportError:
        return "Error: Please install whisper with: pip install openai-whisper"
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

def analyze_image_gemini(image_path):
    """Analyze image using Google Gemini Vision (Free tier)"""
    load_dotenv()
    
    try:
        import google.generativeai as genai
        from PIL import Image
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Load and prepare image
        image = Image.open(image_path)
        
        prompt = """Analyze this travel-related image and provide:
        1. What you see in the image
        2. Potential travel destination or location
        3. Travel tips or recommendations based on what you see
        4. Estimated costs if it's a tourist attraction
        """
        
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def analyze_image_huggingface(image_path):
    """Analyze image using Hugging Face Vision models (Free)"""
    load_dotenv()
    
    try:
        import requests
        from PIL import Image
        import io
        
        # Convert image to bytes
        image = Image.open(image_path)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Use Hugging Face Image-to-Text model
        API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        
        response = requests.post(API_URL, headers=headers, data=img_byte_arr)
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            caption = result[0].get('generated_text', 'Unable to analyze image')
            return f"Image analysis: {caption}\n\nThis appears to be a travel-related image. Consider this location for your travel plans!"
        else:
            return "Unable to analyze the image. Please try again."
            
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def analyze_image(image_path):
    """Try multiple free image analysis APIs"""
    
    # Try Gemini
    if os.getenv("GEMINI_API_KEY"):
        result = analyze_image_gemini(image_path)
        if not result.startswith("Error"):
            return result
    
    # Try Hugging 
    if os.getenv("HUGGINGFACE_API_KEY"):
        result = analyze_image_huggingface(image_path)
        if not result.startswith("Error"):
            return result
    
    return "Error: No valid API keys found for image analysis. Please set GEMINI_API_KEY or HUGGINGFACE_API_KEY."