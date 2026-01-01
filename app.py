import streamlit as st
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import google.generativeai as genai
from groq import Groq
import json
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Critic Mind AI",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Sidebar for Model Selection
with st.sidebar:
    st.title("⚙️ AI Settings")
    model_choice = st.radio("Select AI Engine", ["Groq (Llama 3)", "Gemini (Flash)"], index=0)
    st.info("Groq is faster, Gemini is more detailed.")

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a1a2e 0%, #050505 100%);
        color: white;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1rem;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #6366f1 0%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #db2777 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.5);
    }
    
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "step" not in st.session_state:
    st.session_state.step = "intro"
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "retry_count" not in st.session_state:
    st.session_state.retry_count = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "summary_data" not in st.session_state:
    st.session_state.summary_data = None

TRAILER_ID = "TcMBFSGVi1c" # Avengers Endgame
QUESTIONS = [
    "What was this movie trailer about?",
    "What did you like in this video?",
    "What was the most memorable scene in the video?"
]

# --- AI LOGIC ---
def validate_response(question, response, retry_count, model_provider):
    # --- TIER 1: LOCAL KEYWORD DETECTION (Always Works) ---
    neg_keywords = ["pacing", "substance", "generic", "noisy", "safe", "crowded", "lacks", "depth", "oversimplified", "limited", "spectacle", "cliché", "cliche", "rushed", "formulaic"]
    pos_keywords = ["love", "epic", "great", "amazing", "wow", "favorite", "the best", "impressive", "striking"]
    
    local_sentiment = "Neutral"
    local_reasoning = "Factual statement detected."
    
    lower_res = response.lower()
    if any(word in lower_res for word in neg_keywords):
        local_sentiment = "Negative"
        local_reasoning = "Detected critical keywords (Local Analysis)."
    elif any(word in lower_res for word in pos_keywords):
        local_sentiment = "Positive"
        local_reasoning = "Detected appreciative keywords (Local Analysis)."

    # --- TIER 2: AI BRAIN (Adds Nuance) ---
    prompt = f"""
    System: You are an AI Validator & Film Critic.
    Context: Avengers Endgame Trailer.
    User Response: "{response}"
    
    TASK 1: VALIDATION (Strict)
    - Gibberish? (Random letters like 'asdf', meaningless). -> isValid: False
    - Unrelated? (Topics not in video: beaches, cooking, sports). -> isValid: False
    - Grammar/Logic? (Must be a coherent sentence, not broken words). -> isValid: False
    
    TASK 2: SENTIMENT (Only if Valid)
    - Negative: Technical critiques ("pacing", "depth", "cliche", "generic", "noisy").
    - Positive: Praise/Interest.
    - Neutral: Facts only.
    
    Output JSON format ONLY: 
    {{
        "isValid": boolean, 
        "reasoning": "Explain validation & sentiment", 
        "followUp": "If invalid, give a 1-sentence hint for the user. If valid, null",
        "sentiment": "Negative/Positive/Neutral"
    }}
    """
    
    try:
        if "Groq" in model_provider:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key: raise Exception("Groq Key Missing")
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            text = chat_completion.choices[0].message.content
        else:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key: raise Exception("Gemini Key Missing")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(prompt)
            text = res.text

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            emoji_map = {"Positive": "⭐", "Negative": "🚩", "Neutral": "😐", "Mixed": "🌓"}
            data["sentiment_emoji"] = emoji_map.get(data.get("sentiment"), "✨")
            return data
    except Exception as e:
        # If AI Fails, use the Local Detection!
        emoji_map = {"Positive": "⭐", "Negative": "🚩", "Neutral": "😐"}
        return {
            "isValid": True, 
            "reasoning": f"AI Link Offline (Error: {str(e)}). {local_reasoning}", 
            "sentiment": local_sentiment, 
            "sentiment_emoji": emoji_map.get(local_sentiment, "✨")
        }

def generate_final_summary(history, model_provider):
    summary_data = "\n".join([f"Q: {h['q']} A: {h['a']}" for h in history])
    prompt = f"""
    Analyze the following user responses from a movie trailer quiz and provide:
    1. A 20-word summary of their overall "vibe" or emotional state.
    2. One movie recommendation based on their interests.
    
    Data:
    {summary_data}
    
    Output JSON format ONLY: {{"overall_vibe": "str", "recommendation": "str"}}
    """
    
    try:
        if "Groq" in model_provider:
            api_key = os.getenv("GROQ_API_KEY")
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            text = completion.choices[0].message.content
        else:
            api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(prompt)
            text = res.text
            
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return {"overall_vibe": "You seem like a true fan of epic cinema!", "recommendation": "Zack Snyder's Justice League"}

# --- UI FLOW ---

if st.session_state.step == "intro":
    st.markdown('<div class="gradient-text">Movie Mind AI</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <p style="font-size: 1.1rem; opacity: 0.8; margin-bottom: 2rem;">
            Watch the official Avengers Endgame trailer using the link below, then return here to share your thoughts with our AI.
        </p>
        <a href="https://www.youtube.com/watch?v={TRAILER_ID}" target="_blank" 
           style="text-decoration: none; display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #db2777 100%); 
                  color: white; padding: 0.8rem 2.5rem; border-radius: 12px; font-weight: 600; font-size: 1.1rem;
                  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3); margin-bottom: 2rem;">
            📺 Open Movie Trailer
        </a>
        <p style="font-size: 0.9rem; color: #888;">Once you finish watching, click the button below to start the quiz.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Proceed to Questions"):
        st.session_state.step = "questions"
        st.rerun()

elif st.session_state.step == "questions":
    idx = st.session_state.q_index
    st.markdown(f'<div class="gradient-text">Conversation</div>', unsafe_allow_html=True)
    
    with st.container():
        # Display progress
        progress = (idx + 1) / len(QUESTIONS)
        st.progress(progress)
        st.markdown(f'<p style="color: #6366f1; font-weight: 600; margin-bottom: 0.5rem; text-align: right;">Step {idx + 1} of 3</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><h3 style="margin:0;">{QUESTIONS[idx]}</h3></div>', unsafe_allow_html=True)
        
        # Unique key for each question to avoid state conflicts
        input_key = f"input_q{idx}_retry{st.session_state.retry_count}"
        user_input = st.text_area("Your Response", key=input_key, height=120, placeholder="Type your answer here...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.session_state.retry_count > 0:
                st.caption(f"Attempt {st.session_state.retry_count + 1}/3")
        
        if st.button("Submit Answer", key=f"submit_{idx}"):
            if not user_input.strip():
                st.warning("Please type something before submitting.")
            else:
                with st.spinner(f"{model_choice} is validating your response..."):
                    result = validate_response(QUESTIONS[idx], user_input, st.session_state.retry_count, model_choice)
                    
                    if result["isValid"]:
                        st.success(f"✅ Input Accepted! Sentiment: {result['sentiment']}")
                        st.session_state.history.append({
                            "q": QUESTIONS[idx], 
                            "a": user_input, 
                            "sentiment": result.get("sentiment", "Neutral"),
                            "emoji": result.get("sentiment_emoji", "✨"),
                            "reasoning": result.get("reasoning", "Processed by AI")
                        })
                        time.sleep(1.5)
                        
                        if st.session_state.q_index < 2:
                            st.session_state.q_index += 1
                            st.session_state.retry_count = 0
                            st.rerun()
                        else:
                            st.session_state.step = "done"
                            st.rerun()
                    else:
                        new_retry = st.session_state.retry_count + 1
                        if new_retry >= 3:
                            st.warning(f"Maximum attempts reached. AI Note: {result['reason']}")
                            st.session_state.history.append({
                                "q": QUESTIONS[idx], 
                                "a": user_input + " (System advanced)",
                                "sentiment": result.get("sentiment", "Mixed"),
                                "emoji": "🤔"
                            })
                            time.sleep(2)
                            if st.session_state.q_index < 2:
                                st.session_state.q_index += 1
                                st.session_state.retry_count = 0
                                st.rerun()
                            else:
                                st.session_state.step = "done"
                                st.rerun()
                        else:
                            st.session_state.retry_count = new_retry
                            st.error(f"🤖 AI Guidance: {result['followUp']}")

elif st.session_state.step == "done":
    st.markdown('<div class="gradient-text">Mission Complete</div>', unsafe_allow_html=True)
    st.balloons()

    if not st.session_state.summary_data:
        with st.spinner(f"{model_choice} is analyzing your cinematic profile..."):
            st.session_state.summary_data = generate_final_summary(st.session_state.history, model_choice)
    


# ... (Previous imports)

# ... (Inside the 'done' step, after summary_data is generated)
    
    with st.container():
        # Display Overall Summary
        sd = st.session_state.summary_data
        st.markdown(f"""
        <div class="glass-card" style="border: 1px solid #db2777; background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(219, 39, 119, 0.1) 100%);">
            <h4 style="margin-top:0; color: #db2777;">🎬 Your Cinematic Identity</h4>
            <p style="font-size: 1.1rem; line-height: 1.6;">{sd.get('overall_vibe', 'You have a deep appreciation for the Avengers saga!')}</p>
            <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1.5rem 0;">
            <p style="font-size: 0.9rem; opacity: 0.7; margin-bottom: 0.5rem;">NEXT WATCH RECOMMENDATION:</p>
            <div style="font-size: 1.3rem; font-weight: 700; color: #6366f1;">🍿 {sd.get('recommendation', 'Spider-Man: No Way Home')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- SENTIMENT PIE CHART ---
        st.markdown('<div class="gradient-text" style="font-size: 1.8rem;">Sentiment Breakdown</div>', unsafe_allow_html=True)
        
        # Calculate counts
        sentiments = [h.get("sentiment", "Neutral") for h in st.session_state.history]
        counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for s in sentiments:
            if s in counts:
                counts[s] += 1
            else:
                counts["Neutral"] += 1 # Group Mixed/Analytical as Neutral for chart simplicity
        
        # Create Chart
        if len(sentiments) > 0:
            labels = []
            sizes = []
            colors = []
            color_map = {"Positive": "#4ade80", "Negative": "#f43f5e", "Neutral": "#94a3b8"}
            
            for k, v in counts.items():
                if v > 0:
                    labels.append(f"{k}")
                    sizes.append(v)
                    colors.append(color_map[k])
            
            fig, ax = plt.subplots(figsize=(5, 5))
            fig.patch.set_alpha(0) # Transparent background
            
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%', 
                startangle=90, 
                colors=colors,
                textprops={'color':"white", 'fontsize': 12, 'weight': 'bold'}
            )
            
            # Make the donut hole (optional, looks premium)
            centre_circle = plt.Circle((0,0),0.70,fc='#0e0e0e')
            fig.gca().add_artist(centre_circle)
            
            ax.axis('equal')  
            st.pyplot(fig)
            
        st.markdown('<div style="text-align: center; margin: 2rem 0 1rem 0;"><h4>Detailed Vibe Check</h4></div>', unsafe_allow_html=True)
        for item in st.session_state.history:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 15px; margin-bottom: 1rem; border-left: 5px solid #6366f1; position: relative;">
                <div style="position: absolute; top: 10px; right: 15px; background: rgba(99, 102, 241, 0.2); padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; border: 1px solid rgba(99, 102, 241, 0.3);">
                    {item.get('emoji', '✨')} {item.get('sentiment', 'Thoughtful')}
                </div>
                <p style="color: #6366f1; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.9rem;">QUESTION: {item['q']}</p>
                <p style="margin: 0; font-size: 1.05rem; opacity: 0.9;">"{item['a']}"</p>
                <p style="margin-top: 0.8rem; font-size: 0.8rem; color: #888; font-style: italic;">AI Logic: {item.get('reasoning', 'Analyzed sentiment based on tone.')}</p>
            </div>
            """, unsafe_allow_html=True)
            
    if st.button("🔄 Restart Experience"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
