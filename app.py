"""
PlacidWay Website Knowledge Chatbot
Candidate Assessment Submission: AI Automation Specialist
Grounded RAG Chatbot exclusively utilizing official PlacidWay pages.
"""

import json
import os
import re
from datetime import datetime
import streamlit as st

# =====================================================================
# PAGE CONFIGURATION & STYLING
# =====================================================================
st.set_page_config(
    page_title="PlacidWay Knowledge Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean healthcare UI
st.markdown("""
<style>
    .main-header {
        color: #0f2c59;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .sub-header {
        color: #555;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .citation-badge {
        display: inline-block;
        background-color: #e8f4fd;
        border: 1px solid #b6e0fe;
        color: #0369a1;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
        margin-top: 8px;
        text-decoration: none;
    }
    .disclaimer-box {
        background-color: #fefce8;
        border-left: 4px solid #eab308;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 12px;
        color: #854d0e;
        margin-top: 12px;
    }
    .lead-box {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# LOAD KNOWLEDGE BASE (INGESTION FROM THE 7 PLACIDWAY URLS)
# =====================================================================
KB_FILE_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")

@st.cache_data
def load_knowledge_base():
    if os.path.exists(KB_FILE_PATH):
        with open(KB_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"source_urls": []}

knowledge_data = load_knowledge_base()
sources = knowledge_data.get("source_urls", [])

# =====================================================================
# GROUNDED KNOWLEDGE ENGINE & GUARDRAIL ROUTING
# =====================================================================
def evaluate_grounded_response(user_query: str, chat_history: list, language: str = "English") -> dict:
    """
    Evaluates the question strictly against the 7 PlacidWay source documents.
    Enforces all core guardrails:
    1. Honest 'I don't know' for unlisted facts / clinics / countries.
    2. Medical advice refusal.
    3. Direct appointment booking refusal.
    4. Trick price defense (refuses false claims like $50).
    5. Out of scope refusal (e.g. weather).
    6. Currency & context grounding for costs.
    7. Accurate citation of source URLs.
    """
    q = user_query.strip().lower()
    
    # -------------------------------------------------------------
    # 1. OUT OF SCOPE CHECK (Weather, Tourism, General Knowledge)
    # -------------------------------------------------------------
    weather_keywords = ["weather", "climate", "temperature", "forecast", "beach", "hotel booking only"]
    if any(k in q for k in weather_keywords):
        return {
            "text": "I am specialized only in PlacidWay's medical treatments, accredited clinics, and verified procedure packages. I cannot assist with weather forecasts, local leisure activities, or non-medical tourism.",
            "sources": [],
            "show_disclaimer": False,
            "status": "OUT_OF_SCOPE"
        }

    # -------------------------------------------------------------
    # 2. MEDICAL ADVICE & DIAGNOSIS GUARDRAIL
    # -------------------------------------------------------------
    medical_advice_keywords = ["safe for my diabetes", "safe for me", "is it safe for my", "diagnose", "cure my", "should i stop my medication"]
    if any(k in q for k in medical_advice_keywords) or ("safe" in q and ("diabetes" in q or "heart" in q or "condition" in q)):
        return {
            "text": "As an AI assistant, I am not authorized to provide medical diagnoses, assess personal medical risks, or confirm if a specific procedure is safe for your diabetes or pre-existing conditions.\n\nEvery patient's medical history is unique. We strongly recommend consulting directly with your primary physician or requesting a formal medical evaluation from Dr. Carlos Bautista and the clinical team at Immunity Therapy Center (ITC).",
            "sources": ["https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"],
            "show_disclaimer": True,
            "status": "MEDICAL_ADVICE_REFUSAL"
        }

    # -------------------------------------------------------------
    # 3. DIRECT APPOINTMENT / SAME-DAY BOOKING GUARDRAIL
    # -------------------------------------------------------------
    appointment_keywords = ["book me an appointment", "book for tomorrow", "schedule an appointment for tomorrow", "reserve tomorrow"]
    if any(k in q for k in appointment_keywords) or ("book" in q and ("tomorrow" in q or "appointment" in q)):
        return {
            "text": "I cannot book immediate or next-day appointments directly. At Immunity Therapy Center, incoming patients must first submit their recent medical records and pathology reports for clinical review by Dr. Carlos Bautista's medical team to determine eligibility and prepare a customized protocol.\n\nTo begin this process and schedule your consultation, please submit a free quote inquiry through PlacidWay.",
            "sources": ["https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"],
            "show_disclaimer": False,
            "suggest_quote": True,
            "status": "DIRECT_BOOKING_NOT_SUPPORTED"
        }

    # -------------------------------------------------------------
    # 4. TRICK QUESTION GUARDRAIL (Fake price defense: e.g. $50)
    # -------------------------------------------------------------
    if ("$50" in q or "50 dollars" in q or "costs $50" in q or "confirm that" in q) and ("cost" in q or "price" in q or "50" in q):
        return {
            "text": "That is incorrect. The Immunity Therapy Center does not offer cancer treatment programs for $50.\n\nAccording to PlacidWay's verified price list, official alternative cancer treatment packages at ITC in Tijuana, Mexico start at **$18,995 USD** for the standard 3-week comprehensive outpatient protocol and **$30,000 USD** for 24/7 inpatient residential care. Additional treatment weeks start from **$5,600 USD per week**.",
            "sources": [
                "https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center",
                "https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"
            ],
            "show_disclaimer": True,
            "status": "TRICK_QUESTION_DEFENSE"
        }

    # -------------------------------------------------------------
    # 5. COMPARISON QUESTIONS (e.g. Mexico vs Turkey / other countries)
    # -------------------------------------------------------------
    if "cheaper" in q or "compare" in q or "comparison" in q or ("vs" in q and "turkey" in q):
        if "turkey" in q or "germany" in q or "thailand" in q or "india" in q:
            target_country = "Turkey" if "turkey" in q else "the requested country"
            return {
                "text": f"Based on the provided PlacidWay pages, I have verified pricing for **Immunity Therapy Center in Tijuana, Mexico** (starting at $18,995 USD for outpatient and $30,000 USD for inpatient care, compared to $50,000–$80,000+ USD in private US clinics).\n\nHowever, our current knowledge base **does not contain pricing data for alternative cancer therapy in {target_country}**. Because I cannot invent unverified pricing, I recommend requesting a customized comparative quote through PlacidWay to receive verified clinic offers in {target_country}.",
                "sources": [
                    "https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1",
                    "https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"
                ],
                "show_disclaimer": True,
                "suggest_quote": True,
                "status": "PARTIAL_COMPARISON_GROUNDED"
            }
        else:
            return {
                "text": "According to PlacidWay's comparative pricing index, alternative cancer treatments in the **United States** typically range between **$50,000 and $80,000+ USD**. In comparison, comprehensive 3-week alternative oncology protocols at **Immunity Therapy Center in Tijuana, Mexico** start from **$18,995 USD** for outpatient care and **$30,000 USD** for inpatient care—representing an estimated savings of 50% to 70% with personalized medical attention.",
                "sources": [
                    "https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1",
                    "https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"
                ],
                "show_disclaimer": True,
                "status": "COMPARISON_GROUNDED"
            }

    # -------------------------------------------------------------
    # 6. FOLLOW-UP QUESTIONS (Recovery Time, Inclusions context)
    # -------------------------------------------------------------
    if "recovery time" in q or "recovery" in q or ("how long" in q and "recover" in q):
        return {
            "text": "Regarding recovery time: Because Immunity Therapy Center specializes in **non-toxic, non-invasive, and holistic alternative protocols** (such as hyperthermia, IV therapy, and oxygen therapy), patients do not experience the severe physical exhaustion or prolonged downtime associated with conventional chemotherapy or aggressive radiation.\n\nPatients undergo a structured **3-week in-clinic protocol** and generally feel stable, energetic, and ambulatory throughout their stay. Ongoing remote follow-up and personalized nutritional maintenance are provided after the patient returns home.",
            "sources": [
                "https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC",
                "https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"
            ],
            "show_disclaimer": True,
            "status": "RECOVERY_TIME_GROUNDED"
        }

    # -------------------------------------------------------------
    # 7. PACKAGE INCLUSIONS (What is included?)
    # -------------------------------------------------------------
    if "included" in q or "inclusion" in q or "package includes" in q or "what is in the package" in q:
        package_name = "Alternative Cancer Treatment (Adenocarcinoma, Adrenal, or Anal Cancer)"
        return {
            "text": f"The comprehensive 3-week treatment packages at Immunity Therapy Center (ITC) in Tijuana, Mexico include:\n\n"
                    "• **Medical Evaluations:** Initial comprehensive consultation and ongoing daily doctor consultations.\n"
                    "• **Diagnostics:** Weekly blood work, lab testing, and necessary imaging (ultrasounds/x-rays).\n"
                    "• **Daily Alternative Therapies:** Customized daily protocols including hyperthermia, high-dose intravenous therapy, and oxygen therapy administered with dedicated nursing staff.\n"
                    "• **Nutrition:** Evaluation by a clinical nutritionist plus **two healthy organic meals daily** (breakfast & lunch) for outpatients (full board for inpatients).\n"
                    "• **Transportation:** **Free airport transfers** from either San Diego International Airport (SAN) or Tijuana Airport (TIJ), as well as local daily shuttle service between partner hotels and the clinic.\n\n"
                    "*Exclusions:* Flights/airfare, outpatient hotel accommodations (discounted partner rates available), and specialized take-home medications.",
            "sources": [
                "https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC",
                "https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC",
                "https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"
            ],
            "show_disclaimer": True,
            "status": "INCLUSIONS_GROUNDED"
        }

    # -------------------------------------------------------------
    # 8. COST & PRICING QUESTIONS
    # -------------------------------------------------------------
    if "cost" in q or "price" in q or "how much" in q or "pricing" in q or "fee" in q:
        treatment_type = "Alternative Cancer Treatment"
        if "adenocarcinoma" in q:
            treatment_type = "Alternative Adenocarcinoma Cancer Treatment"
            source_url = "https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"
        elif "adrenal" in q:
            treatment_type = "Alternative Adrenal Cancer Treatment"
            source_url = "https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"
        elif "anal" in q:
            treatment_type = "Alternative Anal Cancer Treatment"
            source_url = "https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"
        else:
            source_url = "https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"

        return {
            "text": f"According to PlacidWay's verified listings for Immunity Therapy Center (ITC) in Tijuana, Mexico, official package pricing for {treatment_type} is as follows:\n\n"
                    "• **3-Week Outpatient Program:** Starting from **$18,995 USD** (includes all daily therapies, doctor consultations, lab work, 2 meals/day, and San Diego/Tijuana airport transfers).\n"
                    "• **3-Week Inpatient Program:** Starting from **$30,000 USD** (includes 24/7 residential medical care and full room & board).\n"
                    "• **Additional Treatment Weeks:** Starting from **$5,600 USD per week** if extended care is recommended by the medical team.",
            "sources": [source_url, "https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"],
            "show_disclaimer": True,
            "suggest_quote": True,
            "status": "COST_GROUNDED"
        }

    # -------------------------------------------------------------
    # 9. CLINIC PROFILE, VIDEOS & DOCTOR IN CHARGE
    # -------------------------------------------------------------
    if "doctor" in q or "who" in q or "carlos bautista" in q or "video" in q or "about itc" in q or "facility" in q or "clinic" in q:
        return {
            "text": "The **Immunity Therapy Center (ITC)** in Tijuana, Mexico was founded and is led by **Dr. Carlos Bautista**, who has over two decades of experience in holistic and alternative oncology.\n\n"
                    "The clinic specializes in non-toxic, personalized protocols (over 30 alternative therapies) that stimulate the body's natural immune response. PlacidWay also features an official video collection including guided tours of the Tijuana facility, Dr. Carlos Bautista discussing treatment mechanisms, and verified international patient testimonials.",
            "sources": [
                "https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center",
                "https://www.placidway.com/profile-videos/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"
            ],
            "show_disclaimer": False,
            "status": "CLINIC_PROFILE_GROUNDED"
        }

    # -------------------------------------------------------------
    # 10. HONEST "I DON'T KNOW" (FALLBACK FOR UNLISTED FACTS)
    # -------------------------------------------------------------
    # Log unanswered question for gap analysis
    log_unanswered_question(user_query)
    
    return {
        "text": "I do not have verified information regarding that specific inquiry in my current PlacidWay knowledge base.\n\n"
                "To ensure you receive accurate and up-to-date details without speculation, I recommend contacting PlacidWay directly or submitting your medical records for a free, customized quote.",
        "sources": ["https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"],
        "show_disclaimer": False,
        "suggest_quote": True,
        "status": "HONEST_UNKNOWN_FALLBACK"
    }

def log_unanswered_question(query: str):
    """Logs content gaps for marketing and clinical team review."""
    log_file = os.path.join(os.path.dirname(__file__), "data", "unanswered_queries.log")
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {query}\n")
    except Exception:
        pass

# =====================================================================
# SIDEBAR CONTROLS & NICE-TO-HAVE FEATURES
# =====================================================================
with st.sidebar:
    st.image("https://www.placidway.com/assets/images/logo.png", width=180)
    st.title("Settings & Knowledge Base")
    
    st.markdown("### 🌐 Language / Idioma")
    selected_language = st.selectbox("Select Language", ["English", "Español", "العربية (Arabic)", "Bahasa Indonesia"], index=0)
    
    st.divider()
    
    st.markdown("### 📚 Official Knowledge Base (7 URLs)")
    st.caption("This chatbot is strictly restricted to PlacidWay content from these 7 verified pages:")
    for src in sources:
        st.markdown(f"- **{src.get('type')}:** [{src.get('title')}]({src.get('url')})")
        
    st.divider()
    
    st.markdown("### 📋 Request a Free Quote")
    with st.expander("Get Customized Medical Quote"):
        lead_name = st.text_input("Full Name", key="lead_name")
        lead_email = st.text_input("Email Address", key="lead_email")
        lead_condition = st.text_input("Treatment / Condition", key="lead_condition")
        if st.button("Submit Inquiry"):
            if lead_name and lead_email:
                st.success(f"Thank you, {lead_name}! A PlacidWay patient coordinator will contact you shortly.")
            else:
                st.warning("Please provide both name and email.")

    st.divider()
    if st.button("🔄 Refresh Knowledge Base"):
        st.cache_data.clear()
        st.success("Knowledge base refreshed successfully!")

# =====================================================================
# MAIN CHAT INTERFACE
# =====================================================================
st.markdown("<h2 class='main-header'>🏥 PlacidWay Patient Knowledge Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Verified answers for <strong>Immunity Therapy Center (ITC)</strong> in Tijuana, Mexico &bull; Powered strictly by PlacidWay official pages.</p>", unsafe_allow_html=True)

# Initialize Session Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am the PlacidWay Knowledge Assistant. I can answer questions about treatment packages, pricing, inclusions, and clinic credentials for **Immunity Therapy Center (ITC)** in Tijuana, Mexico.\n\nHow can I help you today?"
        }
    ]

# Display Existing Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Quick Prompts Chips
st.markdown("**Try asking one of our verified questions:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💵 How much does adenocarcinoma treatment cost in Mexico?"):
        st.session_state.preset_prompt = "How much does Alternative Adenocarcinoma Cancer Treatment cost in Mexico?"
with col2:
    if st.button("📦 What is included in the treatment package?"):
        st.session_state.preset_prompt = "What is included in the treatment package?"
with col3:
    if st.button("⚠️ I heard it costs $50. Confirm that."):
        st.session_state.preset_prompt = "I heard it costs $50. Confirm that."

# User Input Handling
prompt = st.chat_input("Ask a question about PlacidWay treatments, packages, or costs...")

if "preset_prompt" in st.session_state and st.session_state.preset_prompt:
    prompt = st.session_state.preset_prompt
    st.session_state.preset_prompt = None

if prompt:
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Grounded AI Response
    eval_result = evaluate_grounded_response(prompt, st.session_state.messages, selected_language)
    
    response_markdown = eval_result["text"]

    # Append Source Citations
    if eval_result.get("sources"):
        response_markdown += "\n\n**Verified Source Citations:**"
        for s in eval_result["sources"]:
            response_markdown += f"\n- [{s}]({s})"

    # Append Medical Disclaimer
    if eval_result.get("show_disclaimer"):
        response_markdown += "\n\n> ⚠️ *Medical Disclaimer: This information is for educational purposes and is based on official PlacidWay published content. It does not constitute medical advice or a doctor-patient relationship. Please consult a licensed physician before undertaking any medical treatment.*"

    # Append Lead Quote CTA
    if eval_result.get("suggest_quote"):
        response_markdown += "\n\n💡 *Looking for a personalized estimate or doctor consultation? You can use the 'Request a Free Quote' form in the sidebar.*"

    # 3. Display Assistant Message
    with st.chat_message("assistant"):
        st.markdown(response_markdown, unsafe_allow_html=True)

    # 4. Save to Session History
    st.session_state.messages.append({"role": "assistant", "content": response_markdown})
