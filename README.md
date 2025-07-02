# 🌍 AI Travel Assistant

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

An intelligent, multimodal travel assistant that helps you plan, book, and manage your trips with ease. Powered by AI, it offers personalized recommendations, budgeting, itinerary planning, and more—all in one place.

---

## ✨ Features
- **AI-Powered Trip Planning**: Get personalized itineraries based on your preferences.
- **Budget Management**: Plan trips within your budget.
- **Booking Assistance**: Book flights, hotels, and activities seamlessly.
- **Multimodal Input**: Supports text and image-based queries.
- **Interactive Maps**: Visualize your journey and destinations.
- **Memory & Context**: Remembers your preferences and past trips.

---

## 📁 Folder Structure
```
AI-Travel-Assistant/
  Agent_AI/
    agents/         # Core AI agents (planner, booking, budgeter)
    utils/          # Utility modules (maps, memory, image generation, etc.)
    workflows/      # Workflow and trip graph logic
    app.py          # Main application entry point
    requirements.txt# Python dependencies
```

---

## 🚀 Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AI-Travel-Assistant.git
   cd AI-Travel-Assistant/Agent_AI
   ```
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🏁 Usage
Run the main application:
```bash
python app.py
```

You can interact with the assistant via the command line or integrate it into your own interface.

---

## 🧳 Example
```
> Where should I travel in June for a beach vacation under $2000?
AI: I recommend Bali, Indonesia! Here's a 7-day itinerary within your budget...
```

---

## 🤝 Contributing
Contributions are welcome! Please open issues or pull requests for new features, bug fixes, or suggestions.

---

## 📄 License
This project is licensed under the MIT License.
