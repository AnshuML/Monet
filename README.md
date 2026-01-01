# 🎬 Critic Mind AI

Critic Mind AI is an intelligent conversational application that evaluates user responses to movie trailers. Using advanced LLMs (Gemini and Groq), it validates user feedback for relevance, logic, and sentiment, providing a personalized cinematic profile.

## Features

- **Video Context Awareness**: Securely integrates with movie trailers (default: Avengers Endgame).
- **Dual AI Engine**: Toggle between **Groq (Llama 3)** for speed and **Gemini (Flash)** for deep analysis.
- **Smart Validation**:
  - Detects gibberish and meaningless input.
  - Ensures contextual relevance (avoids off-topic comments like "I like beaches").
  - Checks for logical and grammatical coherence.
- **Sentiment Analysis**: Accurately categorizes feedback into **Positive ⭐**, **Negative 🚩**, and **Neutral 😐** or **Mixed 🌓**.
- **Visual Analytics**: Generates a real-time **Sentiment Breakdown Pie Chart** based on your session.
- **Cinematic Identity**: Provides a summarized emotional "vibe check" and personalized movie recommendations.

##  Tech Stack

- **Frontend**: Streamlit (Premium Glassmorphism UI)
- **AI/LLM**: Google Gemini 1.5 Flash, Groq (Llama 3.3 70B)
- **Data Viz**: Matplotlib
- **Environment**: Python 3.10+

##  Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/AnshuML/Monet.git
cd monteck
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory and add your API keys:
```env
GEMINI_API_KEY="your_gemini_key"
GROQ_API_KEY="your_groq_key"
```

### 5. Run the app
```bash
streamlit run app.py
```

##  How it Works

1. **Watch**: The user watches a provided movie trailer.
2. **Interact**: The system asks 3 open-ended questions about the experience.
3. **Validate**: The AI checks if the response is "inline" with the trailer content. If invalid, the user receives one of 3 guiding follow-up prompts.
4. **Summary**: After completion, a final profile is generated with sentiment analytics and recommendations.

## 📄 Assignment Compliance

This project fulfills all requirements for the AI/ML Practical Assignment:
- [x] Movie trailer integration.
- [x] Sequential 3-question flow.
- [x] Gibberish and relevance detection.
- [x] Logical/Grammar validation.
- [x] 3-retry limit with guiding follow-ups.
- [x] Forced progression logic.

---
Built with by [Anshu](https://github.com/AnshuML)
