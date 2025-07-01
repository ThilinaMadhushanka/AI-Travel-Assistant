import streamlit as st
from workflows.trip_graph import plan_trip
from utils.multimodal_input import transcribe_audio_free, analyze_image
from utils.image_generation import get_enhanced_destination_visuals, display_enhanced_images_streamlit, get_google_images_urls
import os
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta, date
import tempfile
import re

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Enhanced Travel Assistant with Smart Inputs",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0
if 'rate_limit_hit' not in st.session_state:
    st.session_state.rate_limit_hit = False
if 'rate_limit_reset_time' not in st.session_state:
    st.session_state.rate_limit_reset_time = None
if 'trip_history' not in st.session_state:
    st.session_state.trip_history = []
if 'destination_images' not in st.session_state:
    st.session_state.destination_images = {}

# Popular destinations by country/region
DESTINATIONS = {
    "🇺🇸 United States": ["New York City", "Los Angeles", "Las Vegas", "Miami", "San Francisco", "Chicago", "Boston", "Washington DC"],
    "🇬🇧 United Kingdom": ["London", "Edinburgh", "Manchester", "Bath", "Oxford", "Cambridge", "Liverpool", "Brighton"],
    "🇫🇷 France": ["Paris", "Nice", "Lyon", "Marseille", "Bordeaux", "Strasbourg", "Toulouse", "Cannes"],
    "🇮🇹 Italy": ["Rome", "Florence", "Venice", "Milan", "Naples", "Bologna", "Turin", "Palermo"],
    "🇪🇸 Spain": ["Madrid", "Barcelona", "Seville", "Valencia", "Bilbao", "Granada", "Toledo", "San Sebastian"],
    "🇩🇪 Germany": ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt", "Dresden", "Heidelberg", "Rothenburg"],
    "🇯🇵 Japan": ["Tokyo", "Kyoto", "Osaka", "Hiroshima", "Nara", "Hakone", "Takayama", "Nikko"],
    "🇹🇭 Thailand": ["Bangkok", "Chiang Mai", "Phuket", "Krabi", "Koh Samui", "Pattaya", "Ayutthaya", "Sukhothai"],
    "🇸🇬 Singapore": ["Marina Bay", "Chinatown", "Little India", "Orchard Road", "Sentosa Island"],
    "🇦🇺 Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast", "Cairns", "Darwin"],
    "🇨🇦 Canada": ["Toronto", "Vancouver", "Montreal", "Quebec City", "Calgary", "Ottawa", "Banff", "Victoria"],
    "🇧🇷 Brazil": ["Rio de Janeiro", "São Paulo", "Salvador", "Brasília", "Recife", "Fortaleza", "Manaus", "Florianópolis"],
    "🇲🇽 Mexico": ["Mexico City", "Cancun", "Playa del Carmen", "Puerto Vallarta", "Guadalajara", "Oaxaca", "Merida", "Tulum"],
    "🇱🇰 Sri Lanka": ["Colombo", "Kandy", "Galle", "Sigiriya", "Nuwara Eliya", "Anuradhapura", "Polonnaruwa", "Ella"],
    "🇮🇳 India": ["Delhi", "Mumbai", "Goa", "Jaipur", "Kerala", "Agra", "Varanasi", "Rishikesh"],
    "🇨🇳 China": ["Beijing", "Shanghai", "Xi'an", "Guilin", "Chengdu", "Hangzhou", "Suzhou", "Zhangjiajie"],
    "🇰🇷 South Korea": ["Seoul", "Busan", "Jeju Island", "Gyeongju", "Incheon", "Daegu", "Andong", "Jeonju"],
    "🇪🇬 Egypt": ["Cairo", "Luxor", "Aswan", "Alexandria", "Hurghada", "Sharm El Sheikh", "Dahab", "Siwa Oasis"],
    "🇿🇦 South Africa": ["Cape Town", "Johannesburg", "Durban", "Port Elizabeth", "Stellenbosch", "Hermanus", "Knysna", "Plettenberg Bay"]
}

# Travel interests
INTERESTS = [
    "🏛️ Culture & History",
    "🍽️ Food & Cuisine", 
    "🏔️ Adventure & Outdoor",
    "🏖️ Beach & Relaxation",
    "🎨 Art & Museums",
    "🌃 Nightlife & Entertainment",
    "🛍️ Shopping",
    "📷 Photography",
    "🚶‍♂️ Walking & Hiking",
    "🏛️ Architecture",
    "🎭 Local Festivals",
    "🌿 Nature & Wildlife",
    "🚢 Luxury Travel",
    "🎒 Budget Backpacking",
    "👨‍👩‍👧‍👦 Family Friendly"
]

def check_api_keys():
    """Check which API keys are available"""
    available_apis = []
    
    if os.getenv("GROQ_API_KEY"):
        available_apis.append("Groq (Recommended)")
    if os.getenv("GEMINI_API_KEY"):
        available_apis.append("Google Gemini")
    if os.getenv("HUGGINGFACE_API_KEY"):
        available_apis.append("Hugging Face")
    
    return available_apis

def format_travel_input(country, destination, budget, currency, interests, start_date, end_date, additional_notes):
    """Format all inputs into a comprehensive travel request"""
    duration = (end_date - start_date).days + 1
    
    travel_request = f"""
I want to plan a trip to {destination}, {country.replace('🏴 ', '').replace('🇺🇸 ', '').replace('🇬🇧 ', '').replace('🇫🇷 ', '').replace('🇮🇹 ', '').replace('🇪🇸 ', '').replace('🇩🇪 ', '').replace('🇯🇵 ', '').replace('🇹🇭 ', '').replace('🇸🇬 ', '').replace('🇦🇺 ', '').replace('🇨🇦 ', '').replace('🇧🇷 ', '').replace('🇲🇽 ', '').replace('🇱🇰 ', '').replace('🇮🇳 ', '').replace('🇨🇳 ', '').replace('🇰🇷 ', '').replace('🇪🇬 ', '').replace('🇿🇦 ', '')} for {duration} days.

**Travel Details:**
- Destination: {destination}, {country}
- Duration: {duration} days ({start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')})
- Budget: {currency} {budget:,}
- Interests: {', '.join(interests)}

**Additional Requirements:**
{additional_notes if additional_notes else 'No additional requirements specified.'}

Please create a comprehensive travel plan including daily itinerary, budget breakdown, and booking recommendations.
"""
    return travel_request.strip()

def display_api_setup_guide():
    """Display setup guide for API keys"""
    st.markdown("""
    ### 🔑 API Setup Guide
    
    To use this app, you need at least one free API key:
    
    | API | Speed | Quality | Image Gen | Setup Link |
    |-----|-------|---------|-----------|-------------|
    | 🚀 **Groq** | Very Fast | High | ❌ | [console.groq.com](https://console.groq.com/) |
    | 🧠 **Gemini** | Medium | Very High | ❌ | [makersuite.google.com](https://makersuite.google.com/app/apikey) |
    | 🤗 **Hugging Face** | Slow | Medium | ✅ | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
    
    **Note:** For AI image generation, you need a Hugging Face API key. Google Images and sample images work without any API keys!
    
    Create a `.env` file with: `GROQ_API_KEY=your_key_here`
    """)

# Sidebar for settings and history
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Status
    available_apis = check_api_keys()
    if available_apis:
        st.success(f"✅ APIs: {len(available_apis)} connected")
        with st.expander("Connected APIs"):
            for api in available_apis:
                st.write(f"• {api}")
        
        # Image generation status
        if os.getenv("HUGGINGFACE_API_KEY"):
            st.info("🎨 AI Image Generation: Available")
        else:
            st.warning("🎨 AI Image Generation: Not available")
            st.info("📸 Google Images: Available")
    else:
        st.error("❌ No API keys found")
    
    # Visual options
    st.subheader("🖼️ Visual Options")
    show_sample_images = st.checkbox("Show Sample Images", value=True, help="Free images from Unsplash")
    show_google_images = st.checkbox("Show Google Search Links", value=True)
    show_ai_images = st.checkbox("Generate AI Images", value=bool(os.getenv("HUGGINGFACE_API_KEY")), 
                                 disabled=not bool(os.getenv("HUGGINGFACE_API_KEY")))
    
    # Input method selection
    st.subheader("📝 Input Method")
    input_method = st.radio(
        "Choose input method:",
        ["Smart Form", "Text", "Audio", "Image + Text"],
        index=0
    )
    
    # Trip history
    if st.session_state.trip_history:
        st.subheader("📚 Recent Trips")
        for i, trip in enumerate(reversed(st.session_state.trip_history[-3:])):
            with st.expander(f"Trip {len(st.session_state.trip_history) - i}"):
                st.write(trip[:100] + "..." if len(trip) > 100 else trip)

# Main content
st.title("🌍 Enhanced Travel Assistant with Smart Planning")
st.markdown("*Powered by free AI APIs - Now with structured inputs and enhanced image search!*")

if not available_apis:
    st.error("⚠️ No API keys configured!")
    display_api_setup_guide()
    st.stop()

# Input section based on selected method
input_text = ""
selected_destination = ""
formatted_input = ""

if input_method == "Smart Form":
    st.markdown("### 🎯 Smart Travel Planning Form")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Destination Selection
        st.subheader("📍 Destination Selection")
        selected_country = st.selectbox(
            "Select Country/Region:",
            list(DESTINATIONS.keys()),
            index=0
        )
        
        selected_destination = st.selectbox(
            "Select Destination:",
            DESTINATIONS[selected_country],
            index=0
        )
    
    with col2:
        # Travel Dates
        st.subheader("📅 Travel Dates")
        start_date = st.date_input(
            "Start Date:",
            value=date.today() + timedelta(days=30),
            min_value=date.today()
        )
        
        end_date = st.date_input(
            "End Date:",
            value=date.today() + timedelta(days=37),
            min_value=start_date
        )
        
        if end_date <= start_date:
            st.error("End date must be after start date!")
    
    # Budget Section
    st.subheader("💰 Budget Planning")
    budget_col1, budget_col2 = st.columns([2, 1])
    
    with budget_col1:
        budget = st.number_input(
            "Total Budget:",
            min_value=100,
            max_value=100000,
            value=2000,
            step=100,
            help="Enter your total travel budget"
        )
    
    with budget_col2:
        currency = st.selectbox(
            "Currency:",
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "LKR", "INR"],
            index=0
        )
    
    # Interests Selection
    st.subheader("🎨 Travel Interests")
    interests = st.multiselect(
        "Select your interests (choose multiple):",
        INTERESTS,
        default=["🏛️ Culture & History", "🍽️ Food & Cuisine"]
    )
    
    # Additional Notes
    st.subheader("📝 Additional Requirements")
    additional_notes = st.text_area(
        "Any specific requirements or preferences:",
        placeholder="e.g., vegetarian food, accessibility needs, specific activities, accommodation preferences...",
        height=100
    )
    
    # Format the input
    if selected_destination and interests and start_date and end_date:
        formatted_input = format_travel_input(
            selected_country, selected_destination, budget, currency, 
            interests, start_date, end_date, additional_notes
        )
        input_text = formatted_input
        
        # Show preview
        with st.expander("📋 Preview Your Request"):
            st.markdown(formatted_input)

elif input_method == "Text":
    st.markdown("### 📝 Describe Your Trip")
    input_text = st.text_area(
        "Where do you want to go and what's your budget?",
        placeholder="Example: I want to visit Japan for 7 days with a budget of $2000. I'm interested in culture, food, and temples.",
        height=120
    )

elif input_method == "Audio":
    st.markdown("### 🎤 Record Your Travel Request")
    st.info("Upload an audio file describing your travel plans!")
    
    audio_file = st.file_uploader(
        "Upload audio file",
        type=['mp3', 'wav', 'm4a', 'ogg'],
        help="Supported formats: MP3, WAV, M4A, OGG"
    )
    
    if audio_file is not None:
        st.audio(audio_file, format='audio/wav')
        
        if st.button("🔄 Transcribe Audio"):
            with st.spinner("Transcribing audio..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                transcription = transcribe_audio_free(tmp_file_path)
                
                os.unlink(tmp_file_path)
                
                if not transcription.startswith("Error"):
                    input_text = transcription
                    st.success("✅ Audio transcribed successfully!")
                    st.write("**Transcription:**", transcription)
                else:
                    st.error(transcription)

elif input_method == "Image + Text":
    st.markdown("### 🖼️ Upload Travel Image")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image_file = st.file_uploader(
            "Upload an image of your destination",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload a photo of where you want to go or what you want to see"
        )
        
        if image_file is not None:
            st.image(image_file, caption="Uploaded Image", use_column_width=True)
    
    with col2:
        additional_text = st.text_area(
            "Additional details about your trip:",
            placeholder="Budget, duration, specific interests, etc.",
            height=200
        )
    
    if image_file is not None and st.button("🔍 Analyze Image"):
        with st.spinner("Analyzing image..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(image_file.getvalue())
                tmp_file_path = tmp_file.name
            
            image_analysis = analyze_image(tmp_file_path)
            
            os.unlink(tmp_file_path)
            
            if not image_analysis.startswith("Error"):
                input_text = f"Image Analysis: {image_analysis}\n\nAdditional Details: {additional_text}"
                st.success("✅ Image analyzed successfully!")
                with st.expander("View Analysis"):
                    st.write(image_analysis)
            else:
                st.error(image_analysis)

# Enhanced Image Preview Section
if input_text or selected_destination:
    destination_for_images = selected_destination if selected_destination else None
    
    # Extract destinations from text if not using smart form
    if not destination_for_images and input_text:
        destinations = re.findall(r'(?:visit|go to|travel to|trip to)\s+([A-Z][a-zA-Z\s,]+?)(?:\s|,|\.|\n|$)', input_text, re.IGNORECASE)
        if destinations:
            destination_for_images = destinations[0].strip().strip(',').strip('.')
    
    if destination_for_images:
        st.markdown("### 🏞️ Destination Preview")
        
        # Generate Google Images URLs immediately
        google_image_urls = get_google_images_urls(destination_for_images, num_images=8)
        
        # Display Google Image search links in a nice grid
        if google_image_urls:
            st.markdown(f"#### 🔍 Google Images for {destination_for_images}")
            
            # Display in 4 columns
            cols = st.columns(4)
            for i, img_data in enumerate(google_image_urls):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div style="
                        border: 2px solid #e0e0e0; 
                        border-radius: 10px; 
                        padding: 15px; 
                        margin-bottom: 10px; 
                        text-align: center; 
                        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    ">
                        <h6 style="margin: 0 0 10px 0; color: #333; font-size: 12px; font-weight: bold;">{img_data['title']}</h6>
                        <a href="{img_data['url']}" target="_blank" style="
                            display: inline-block; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; 
                            padding: 8px 16px; 
                            text-decoration: none; 
                            border-radius: 25px;
                            font-size: 11px;
                            font-weight: 600;
                            transition: all 0.3s ease;
                            border: none;
                        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                            🖼️ View Images
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Load additional images button
        if st.button(f"🔍 Load More Visual Content for {destination_for_images}"):
            with st.spinner("Loading visual content..."):
                visual_data = get_enhanced_destination_visuals(
                    destination_for_images, 
                    include_ai_generation=show_ai_images,
                    use_streamlit_display=True 
                )
                st.session_state.destination_images[destination_for_images] = visual_data

# Enhanced tips section
with st.expander("💡 Smart Planning Tips"):
    st.markdown("""
    **Using Smart Form (Recommended):**
    - Select from curated destinations for better results
    - Choose multiple interests for personalized recommendations
    - Set realistic budget based on destination
    - Plan at least 3-7 days for comprehensive itineraries
    
    **Budget Guidelines by Region:**
    - **Southeast Asia**: $30-80/day
    - **Europe**: $80-150/day  
    - **North America**: $100-200/day
    - **Japan**: $80-180/day
    - **Australia**: $100-180/day
    
    **Visual Features:**
    - Google Images work instantly without API keys
    - Click any image link to see real photos of your destination
    - AI images require Hugging Face API key
    - Sample images from Unsplash load automatically
    
    **Best Practices:**
    - Book flights 2-3 months in advance for better prices
    - Consider shoulder season for fewer crowds and lower costs
    - Mix interests for a well-rounded experience
    - Add extra 20% to your budget for unexpected expenses
    """)

# Trip planning button and processing
if st.button("🚀 Plan My Trip", type="primary", use_container_width=True):
    if not input_text.strip():
        st.warning("Please provide your travel request first!")
        st.stop()
    
    current_time = time.time()
    time_since_last_request = current_time - st.session_state.last_request_time
    
    min_delay = 30
    if time_since_last_request < min_delay:
        remaining_time = int(min_delay - time_since_last_request)
        st.warning(f"⏳ Please wait {remaining_time} seconds to avoid rate limits.")
        st.stop()
    
    try:
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🗓️ Creating your personalized itinerary...")
            progress_bar.progress(25)
            
            result = plan_trip({"input": input_text})
            
            progress_bar.progress(75)
            status_text.text("🖼️ Preparing destination visuals...")
            
            # Auto-load images for selected destination
            if selected_destination and selected_destination not in st.session_state.destination_images:
                try:
                    visual_data = get_enhanced_destination_visuals(
                        selected_destination, 
                        include_ai_generation=show_ai_images,
                        use_streamlit_display=False  
                    )
                    st.session_state.destination_images[selected_destination] = visual_data
                except:
                    pass 
            
            progress_bar.progress(100)
            status_text.text("✅ Trip planning complete!")
            time.sleep(1)
            progress_container.empty()
        
        # Update session state
        st.session_state.last_request_time = time.time()
        st.session_state.rate_limit_hit = False
        st.session_state.rate_limit_reset_time = None
        st.session_state.trip_history.append(input_text[:200] + "..." if len(input_text) > 200 else input_text)
        
        st.markdown("## 🎯 Your Complete Travel Plan")
        
        # Create enhanced tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Itinerary", "💰 Budget", "🎫 Booking", "🖼️ Visuals", "📱 Summary"])
        
        with tab1:
            st.markdown("### 🗓️ Day-by-Day Itinerary")
            if result.get('planner_output'):
                st.markdown(result['planner_output'])
            else:
                st.warning("Itinerary not generated")
        
        with tab2:
            st.markdown("### 💰 Budget Breakdown")
            if result.get('budgeter_output'):
                st.markdown(result['budgeter_output'])
            else:
                st.warning("Budget not generated")
        
        with tab3:
            st.markdown("### 🎫 Booking Recommendations")
            if result.get('booking_output'):
                st.markdown(result['booking_output'])
            else:
                st.warning("Booking info not generated")
        
        with tab4:
            st.markdown("### 🖼️ Destination Gallery")
            
            # Show Google Images for selected destination
            if selected_destination:
                google_urls = get_google_images_urls(selected_destination, num_images=6)
                if google_urls:
                    st.markdown(f"#### 🔍 {selected_destination} Image Gallery")
                    cols = st.columns(3)
                    for i, img_data in enumerate(google_urls):
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div style="
                                border: 1px solid #ddd; 
                                border-radius: 8px; 
                                padding: 12px; 
                                text-align: center; 
                                background: #fdfdfd; 
                                margin-bottom: 10px;
                            ">
                                <h6 style="margin: 0 0 8px 0; color: #333; font-size: 13px;">{img_data['title']}</h6>
                                <a href="{img_data['url']}" target="_blank" style="
                                    display: inline-block; 
                                    background: linear-gradient(135deg, #4285f4, #34a853); 
                                    color: white; 
                                    padding: 8px 14px; 
                                    text-decoration: none; 
                                    border-radius: 20px;
                                    font-size: 12px;
                                    font-weight: 500;
                                ">🔗 View Images</a>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Show loaded visual content
            if st.session_state.destination_images:
                for dest, visual_data in st.session_state.destination_images.items():
                    display_enhanced_images_streamlit(
                        dest, 
                        visual_data.get('google_urls', []), 
                        visual_data.get('generated_images', []), 
                        visual_data.get('sample_urls', [])
                    )
                    st.markdown("---")
            else:
                st.info("💡 Use the 'Load More Visual Content' button above to see additional images!")
        
        with tab5:
            st.markdown("### 📋 Trip Summary")
            
            # Display trip metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if input_method == "Smart Form" and selected_destination:
                    st.metric("Destination", selected_destination)
                    if 'start_date' in locals() and 'end_date' in locals():
                        duration = (end_date - start_date).days + 1
                        st.metric("Duration", f"{duration} days")
                else:
                    st.metric("Input Method", input_method)
                    st.metric("Request Length", f"{len(input_text)} chars")
            
            with col2:
                if input_method == "Smart Form":
                    st.metric("Budget", f"{currency} {budget:,}" if 'budget' in locals() else "Not set")
                    st.metric("Interests", f"{len(interests)}" if 'interests' in locals() else "0")
                else:
                    st.metric("APIs Available", len(available_apis))
                    st.metric("Images Loaded", len(st.session_state.destination_images))
            
            with col3:
                st.write("**Generated:**")
                st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.write("**Status:**")
                st.success("✅ Complete")
            
            # Original request
            with st.expander("📝 Original Request"):
                st.write(input_text[:500] + "..." if len(input_text) > 500 else input_text)
            
            # Export functionality
            st.markdown("### 📤 Export Your Plan")
            
            export_data = f"""
# Travel Plan Export
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Destination:** {selected_destination if selected_destination else "Multiple destinations"}

## Original Request
{input_text}

## Itinerary
{result.get('planner_output', 'Not generated')}

## Budget
{result.get('budgeter_output', 'Not generated')}

## Booking Information
{result.get('booking_output', 'Not generated')}
            """
            
            st.download_button(
                label="📄 Download Complete Plan",
                data=export_data,
                file_name=f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        
        if "rate limit" in str(e).lower() or "429" in str(e):
            st.session_state.rate_limit_hit = True
            st.session_state.rate_limit_reset_time = datetime.now() + timedelta(minutes=15)
            st.warning("Rate limit reached. Please wait 15 minutes before trying again.")
        
        st.markdown("### 🛠️ Troubleshooting")
        st.info("""
        **If you're seeing errors, try:**
        1. Wait a few minutes and try again (rate limits)
        2. Use the Smart Form for better results
        3. Check your API keys in the sidebar
        4. Simplify your request
        5. Try a different input method
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    🌍 Free Travel Assistant | Powered by Open Source APIs<br>
    Made with ❤️ using Streamlit | No premium subscriptions required
</div>
""", unsafe_allow_html=True)