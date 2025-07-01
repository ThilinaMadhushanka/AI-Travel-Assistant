import os
import requests
import time
from dotenv import load_dotenv
from urllib.parse import quote
import random
import base64
import streamlit as st

# Location-specific image prompts and styles
LOCATION_STYLES = {
    # Asian destinations
    "tokyo": {
        "styles": ["cherry blossoms, modern skyline", "neon lights, bustling streets", "traditional temples", "mount fuji view"],
        "time_of_day": ["golden hour", "blue hour", "night photography"],
        "specific_features": ["Shibuya crossing", "traditional architecture", "zen gardens", "bullet trains"]
    },
    "kyoto": {
        "styles": ["traditional temples", "bamboo forests", "geisha districts", "zen gardens"],
        "time_of_day": ["golden hour", "morning mist", "sunset"],
        "specific_features": ["torii gates", "pagodas", "traditional wooden houses", "stone lanterns"]
    },
    "bangkok": {
        "styles": ["golden temples", "floating markets", "tuk-tuks", "street food scenes"],
        "time_of_day": ["golden hour", "tropical sunset", "vibrant day"],
        "specific_features": ["wat temples", "long-tail boats", "street markets", "thai architecture"]
    },
    
    # European destinations
    "paris": {
        "styles": ["eiffel tower", "cobblestone streets", "cafe culture", "seine river"],
        "time_of_day": ["golden hour", "blue hour", "romantic evening"],
        "specific_features": ["haussmanian architecture", "art nouveau", "bridge reflections", "bistros"]
    },
    "rome": {
        "styles": ["ancient ruins", "cobblestone streets", "renaissance architecture", "fountain squares"],
        "time_of_day": ["golden hour", "warm afternoon light", "dramatic sunset"],
        "specific_features": ["colosseum", "roman columns", "vatican architecture", "piazzas"]
    },
    "london": {
        "styles": ["victorian architecture", "red buses", "royal palaces", "thames river"],
        "time_of_day": ["moody overcast", "golden hour", "dramatic clouds"],
        "specific_features": ["big ben", "telephone boxes", "georgian squares", "bridges"]
    },
    
    # American destinations
    "new york": {
        "styles": ["towering skyscrapers", "urban canyons", "central park", "brooklyn bridge"],
        "time_of_day": ["golden hour", "blue hour", "night cityscape"],
        "specific_features": ["manhattan skyline", "yellow taxis", "fire escapes", "street art"]
    },
    "san francisco": {
        "styles": ["golden gate bridge", "rolling hills", "victorian houses", "cable cars"],
        "time_of_day": ["golden hour", "foggy morning", "sunset"],
        "specific_features": ["painted ladies", "steep streets", "bay views", "pier 39"]
    },
    
    # Tropical/Beach destinations
    "bali": {
        "styles": ["rice terraces", "hindu temples", "tropical beaches", "jungle waterfalls"],
        "time_of_day": ["golden hour", "tropical sunset", "misty morning"],
        "specific_features": ["pura temples", "traditional gates", "volcanic mountains", "palm trees"]
    },
    "maldives": {
        "styles": ["overwater bungalows", "crystal clear lagoons", "coral reefs", "pristine beaches"],
        "time_of_day": ["golden hour", "turquoise day", "romantic sunset"],
        "specific_features": ["stilted villas", "infinity pools", "seaplanes", "beach swings"]
    }
}

def get_location_keywords(destination):
    """Extract location-specific keywords and style preferences"""
    dest_lower = destination.lower()
    
    # Direct match from predefined styles
    for location, styles in LOCATION_STYLES.items():
        if location in dest_lower:
            return styles
    
    # Country/region based matching
    region_keywords = {
        "japan": {"styles": ["traditional temples", "cherry blossoms", "zen gardens"], "time_of_day": ["golden hour"]},
        "thailand": {"styles": ["golden temples", "tropical", "floating markets"], "time_of_day": ["golden hour"]},
        "france": {"styles": ["elegant architecture", "cafes", "romantic"], "time_of_day": ["golden hour"]},
        "italy": {"styles": ["renaissance architecture", "piazzas", "ancient ruins"], "time_of_day": ["warm light"]},
        "usa": {"styles": ["modern cityscape", "diverse landscapes"], "time_of_day": ["golden hour"]},
        "uk": {"styles": ["victorian architecture", "countryside"], "time_of_day": ["dramatic lighting"]},
        "indonesia": {"styles": ["tropical paradise", "temples", "rice terraces"], "time_of_day": ["tropical sunset"]},
        "sri lanka": {"styles": ["ancient temples", "tea plantations", "tropical beaches"], "time_of_day": ["golden hour"]},
    }
    
    for country, styles in region_keywords.items():
        if country in dest_lower:
            return styles
    
    # Generic travel styles
    return {
        "styles": ["beautiful landscape", "travel destination", "scenic view"],
        "time_of_day": ["golden hour", "scenic lighting"],
        "specific_features": ["landmarks", "local culture", "natural beauty"]
    }

def generate_location_specific_prompts(destination, num_prompts=4):
    """Generate location-specific prompts for image generation"""
    location_data = get_location_keywords(destination)
    
    prompts = []
    styles = location_data.get("styles", [])
    times = location_data.get("time_of_day", ["golden hour"])
    features = location_data.get("specific_features", [])
    
    # Base quality and style modifiers
    quality_terms = [
        "professional travel photography",
        "high resolution, detailed",
        "award winning photography", 
        "national geographic style",
        "stunning composition"
    ]
    
    photographic_styles = [
        "wide angle landscape",
        "architectural photography",
        "street photography style",
        "travel documentary style",
        "cinematic composition"
    ]
    
    # Generate diverse prompts
    for i in range(num_prompts):
        base_elements = []
        
        # Add destination
        base_elements.append(destination)
        
        # Add location-specific style
        if styles:
            base_elements.append(random.choice(styles))
        
        # Add time/lighting
        if times:
            base_elements.append(random.choice(times))
        
        # Add specific features occasionally
        if features and random.random() > 0.5:
            base_elements.append(random.choice(features))
        
        # Add quality and style
        base_elements.append(random.choice(quality_terms))
        base_elements.append(random.choice(photographic_styles))
        
        # Additional enhancement terms
        enhancement_terms = [
            "vibrant colors", "sharp focus", "beautiful lighting",
            "professional composition", "travel magazine quality",
            "breathtaking view", "iconic perspective"
        ]
        base_elements.append(random.choice(enhancement_terms))
        
        # Combine into prompt
        prompt = ", ".join(base_elements)
        
        # Add negative prompts for better quality
        negative_terms = "blurry, low quality, distorted, amateur, poor lighting, oversaturated"
        
        prompts.append({
            "positive": prompt,
            "negative": negative_terms,
            "style_focus": styles[i % len(styles)] if styles else "scenic view"
        })
    
    return prompts

def generate_image_huggingface_enhanced(destination, style_preference="scenic"):
    """Enhanced image generation with location-specific prompts"""
    load_dotenv()
    
    # Enhanced model list with better quality models
    models = [
        "stabilityai/stable-diffusion-2-1",
        "runwayml/stable-diffusion-v1-5", 
        "dreamlike-art/dreamlike-diffusion-1.0",
        "prompthero/openjourney-v4",
        "wavymulder/Analog-Diffusion"
    ]
    
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    # Generate location-specific prompts
    prompt_data = generate_location_specific_prompts(destination, 1)[0]
    
    for model in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            
            payload = {
                "inputs": prompt_data["positive"],
                "parameters": {
                    "num_inference_steps": 25,  
                    "guidance_scale": 8.0,     
                    "width": 768,
                    "height": 512,
                    "seed": random.randint(0, 2147483647)
                }
            }
            
            # Add negative prompt if model supports it
            if "stable-diffusion" in model:
                payload["parameters"]["negative_prompt"] = prompt_data["negative"]
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                return {
                    "image_data": response.content,
                    "prompt_used": prompt_data["positive"],
                    "style_focus": prompt_data["style_focus"],
                    "model_used": model
                }
            elif response.status_code == 503:
                time.sleep(15)  
                continue
            else:
                continue
                
        except Exception as e:
            st.warning(f"Model {model} failed: {str(e)}")
            continue
    
    return None

def generate_multiple_destination_images(destination, count=3, style_preferences=None):
    """Generate multiple images for a destination with different styles"""
    if not style_preferences:
        style_preferences = ["scenic", "cultural", "architectural"]
    
    generated_images = []
    
    # Get multiple prompt variations
    prompt_variations = generate_location_specific_prompts(destination, count)
    
    for i, prompt_data in enumerate(prompt_variations):
        st.info(f"🎨 Generating image {i+1}/{count}: {prompt_data['style_focus']}")
        
        load_dotenv()
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        
        # Try different models for variety
        models = [
            "stabilityai/stable-diffusion-2-1",
            "runwayml/stable-diffusion-v1-5",
            "dreamlike-art/dreamlike-diffusion-1.0"
        ]
        
        for model in models:
            try:
                API_URL = f"https://api-inference.huggingface.co/models/{model}"
                
                payload = {
                    "inputs": prompt_data["positive"],
                    "parameters": {
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5 + (i * 0.5), 
                        "seed": random.randint(0, 2147483647)
                    }
                }
                
                response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
                
                if response.status_code == 200:
                    generated_images.append({
                        "image_data": response.content,
                        "prompt": prompt_data["positive"],
                        "style": prompt_data["style_focus"],
                        "model": model
                    })
                    break
                elif response.status_code == 503:
                    time.sleep(10)
                    continue
                    
            except Exception as e:
                continue
        
        # Add delay between generations
        if i < count - 1:
            time.sleep(3)
    
    return generated_images

def display_enhanced_images_streamlit(destination, google_urls, generated_images=None, sample_urls=None):
    """Enhanced display with better organization and metadata"""
    
    st.markdown(f"### 🖼️ Visual Guide to {destination}")
    
    # AI Generated Images with enhanced display
    if generated_images:
        st.markdown("#### 🎨 AI Generated Travel Views")
        
        # Create columns based on number of images
        num_images = len(generated_images)
        if num_images > 0:
            cols = st.columns(min(num_images, 3))
            
            for i, img_data in enumerate(generated_images):
                with cols[i % 3]:
                    try:
                        if isinstance(img_data, dict):
                            st.image(
                                img_data["image_data"], 
                                caption=f"🎨 {img_data.get('style', 'AI Generated')}", 
                                use_container_width=True
                            )
                            
                            # Show generation details in expander
                            with st.expander(f"ℹ️ Image {i+1} Details"):
                                st.write(f"**Style Focus:** {img_data.get('style', 'General')}")
                                st.write(f"**Model:** {img_data.get('model', 'Unknown')}")
                                st.write(f"**Prompt:** {img_data.get('prompt', 'N/A')[:100]}...")
                        else:
                            # Handle old format
                            st.image(
                                img_data, 
                                caption=f"AI Generated: {destination}", 
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Failed to display AI image {i+1}: {str(e)}")
    
    # Sample Images Section
    if sample_urls:
        st.markdown("#### 📸 Sample Travel Photos")
        
        working_urls = get_working_image_urls(sample_urls, max_test=6)
        
        if working_urls:
            cols = st.columns(min(len(working_urls), 3))
            
            for i, img_url in enumerate(working_urls[:6]):
                with cols[i % 3]:
                    try:
                        st.image(
                            img_url, 
                            caption=f"📸 {destination} - View {i+1}", 
                            use_container_width=True
                        )
                    except Exception as e:
                        st.markdown(f"""
                        <div style="border: 2px solid #ddd; padding: 25px; text-align: center; border-radius: 10px; background: linear-gradient(135deg, #f8f9fa, #e9ecef);">
                            <p style="margin: 0; color: #666;">🖼️ Sample Image {i+1}</p>
                            <a href="{img_url}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: 500;">View Full Image</a>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Google Images Section
    if google_urls:
        st.markdown("#### 🔍 Search for More Images")
        
        cols = st.columns(3)
        for i, img_data in enumerate(google_urls):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 10px; text-align: center; background: #f9f9f9;">
                    <h6 style="margin: 0 0 8px 0; color: #333; font-size: 12px;">{img_data['title']}</h6>
                    <a href="{img_data['url']}" target="_blank" style="
                        display: inline-block; 
                        background: #4285f4; 
                        color: white; 
                        padding: 6px 12px; 
                        text-decoration: none; 
                        border-radius: 4px;
                        font-size: 11px;
                    ">🔗 Search</a>
                </div>
                """, unsafe_allow_html=True)

# Helper functions 
def get_sample_images_urls(destination):
    """Get sample image URLs from multiple free image services"""
    clean_destination = destination.lower().replace(' ', '-').replace(',', '')
    
    base_urls = []
    
    # Picsum with destination-based seeds
    picsum_urls = [
        f"https://picsum.photos/800/600?random={hash(destination + str(i)) % 1000}"
        for i in range(4)
    ]
    
    
    # Try Unsplash Source API
    try:
        unsplash_source_urls = [
            f"https://source.unsplash.com/800x600/?{clean_destination},travel,{i}"
            for i in range(4)
        ]
        base_urls.extend(unsplash_source_urls)
    except:
        pass
    base_urls.extend(picsum_urls)
    
    return base_urls[:8]

def get_google_images_urls(destination, num_images=6):
    """Generate Google Images search URLs for travel destinations"""
    search_queries = [
        f"{destination} travel destination",
        f"{destination} tourist attractions", 
        f"{destination} beautiful places",
        f"{destination} landmarks",
        f"{destination} scenic views",
        f"{destination} must visit places"
    ]
    
    base_url = "https://www.google.com/search?q={}&tbm=isch"
    
    urls = []
    for i, query in enumerate(search_queries[:num_images]):
        encoded_query = quote(query)
        url = base_url.format(encoded_query)
        urls.append({
            'title': query.title(),
            'url': url,
            'query': query
        })
    
    return urls

def test_image_url(url, timeout=5):
    """Test if an image URL is accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def get_working_image_urls(urls, max_test=4):
    """Filter URLs to only return working image URLs"""
    working_urls = []
    
    for i, url in enumerate(urls[:max_test]):
        try:
            if test_image_url(url):
                working_urls.append(url)
            if len(working_urls) >= 4:
                break
        except:
            continue
    
    if not working_urls:
        working_urls = [
            "https://picsum.photos/800/600?random=1",
            "https://picsum.photos/800/600?random=2", 
            "https://picsum.photos/800/600?random=3",
            "https://picsum.photos/800/600?random=4"
        ]
    
    return working_urls

def get_enhanced_destination_visuals(destination, include_ai_generation=True, use_streamlit_display=True):
    """Enhanced main function with better AI generation"""
    result = {
        'google_urls': [],
        'generated_images': [],
        'sample_urls': [],
        'html_gallery': '',
        'success': False
    }
    
    try:
        # Get Google search URLs
        google_urls = get_google_images_urls(destination)
        result['google_urls'] = google_urls
        
        # Get sample images
        try:
            sample_urls = get_sample_images_urls(destination)
            result['sample_urls'] = sample_urls
        except Exception as e:
            st.warning(f"Sample images service temporarily unavailable")
            result['sample_urls'] = []
        
        # Enhanced AI image generation
        generated_images = []
        if include_ai_generation and os.getenv('HUGGINGFACE_API_KEY'):
            try:
                st.info(f"🎨 Generating location-specific AI images for {destination}...")
                
                # Generate multiple images with different styles
                generated_images = generate_multiple_destination_images(destination, count=3)
                
                if generated_images:
                    st.success(f"✅ Generated {len(generated_images)} AI images for {destination}")
                else:
                    st.warning("")
                    
            except Exception as e:
                st.warning(f"AI image generation encountered an issue: {str(e)}")
        
        result['generated_images'] = generated_images
        
        # Display images
        if use_streamlit_display:
            display_enhanced_images_streamlit(destination, google_urls, generated_images, result['sample_urls'])
        
        result['success'] = True
        return result
        
    except Exception as e:
        result['error'] = str(e)
        st.error(f"Error loading visuals for {destination}: {str(e)}")
        
        # Fallback to Google Images only
        try:
            result['google_urls'] = get_google_images_urls(destination)
        except:
            pass
            
        return result