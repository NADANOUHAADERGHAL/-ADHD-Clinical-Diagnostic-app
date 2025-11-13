import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
from datetime import datetime
import os

# -------------------------------
# Translator functions
# -------------------------------
def translate_text(text, target_lang):
    if target_lang == "العربية":
        lang_code = "ar"
    elif target_lang == "Français":
        lang_code = "fr"
    else:
        lang_code = "en"
    return GoogleTranslator(source='auto', target=lang_code).translate(text)

def translate_to_english(text):
    return GoogleTranslator(source='auto', target='en').translate(text)

# -------------------------------
# Streamlit app
# -------------------------------
st.set_page_config(page_title="ADHD Clinical Form", page_icon="🧠", layout="centered")
st.title("🧠 ADHD Clinical Diagnostic Form (DSM-5 & Vanderbilt)")

# -------------------------------
# 1. LANGUAGE SELECTION
# -------------------------------
language = st.selectbox(
    "Choose your language / اختر لغتك / Choisissez votre langue:",
    ["English", "العربية", "Français"]
)

patient_type = st.radio("Who is filling this form?", ["Adult (self)", "Parent (for child)"])

# -------------------------------
# 2. PATIENT INFORMATION
# -------------------------------
st.header("👤 Patient Information")
name = st.text_input("Full Name / الاسم الكامل / Nom complet")
age = st.number_input("Age / العمر / Âge", min_value=3, max_value=99)
gender = st.selectbox("Gender / الجنس / Sexe", ["Male", "Female"])
country = st.text_input("Country / البلد / Pays")

# -------------------------------
# 3. ADHD CORE SYMPTOMS (DSM-5)
# -------------------------------
st.header("📌 ADHD Core Symptoms")

inattention_questions = [
    "Often fails to give close attention to details or makes careless mistakes.",
    "Often has difficulty sustaining attention in tasks or play activities.",
    "Often does not seem to listen when spoken to directly.",
    "Often does not follow through on instructions and fails to finish tasks.",
    "Often has difficulty organizing tasks and activities.",
    "Often avoids or dislikes tasks requiring sustained mental effort.",
    "Often loses things necessary for tasks (e.g., keys, homework).",
    "Is often easily distracted by extraneous stimuli.",
    "Is often forgetful in daily activities."
]

hyperactivity_questions = [
    "Often fidgets or taps hands/feet or squirms in seat.",
    "Often leaves seat in situations when remaining seated is expected.",
    "Often runs or climbs in situations where it is inappropriate.",
    "Often unable to play or engage in activities quietly.",
    "Is often 'on the go' or acts as if 'driven by a motor.'",
    "Often talks excessively.",
    "Often blurts out answers before questions have been completed.",
    "Often has difficulty waiting his or her turn.",
    "Often interrupts or intrudes on others."
]

all_questions = inattention_questions + hyperactivity_questions

options = {
    "English": ["Never", "Rarely", "Sometimes", "Often", "Very Often"],
    "العربية": ["أبداً", "نادراً", "أحياناً", "كثيراً", "كثيراً جداً"],
    "Français": ["Jamais", "Rarement", "Parfois", "Souvent", "Très souvent"]
}

answers = []
for q in all_questions:
    translated_q = translate_text(q, language)
    ans = st.selectbox(translated_q, options[language], key=q)
    answers.append(ans)

# -------------------------------
# 4. COMORBIDITIES / ADDITIONAL INFO
# -------------------------------
st.header("⚕️ Additional Information / Comorbidities")

comorbidity_questions = [
    "Any sleep problems?",
    "Any mood or anxiety issues?",
    "Any learning difficulties?",
    "Family history of ADHD?",
]

comorbidity_answers = []
for q in comorbidity_questions:
    translated_q = translate_text(q, language)
    ans = st.selectbox(translated_q, ["No", "Yes", "Not sure"], key=q)
    comorbidity_answers.append(ans)

# -------------------------------
# 5. ADHD DIAGNOSIS STATUS
# -------------------------------
st.header("🧩 ADHD Diagnosis Status")

diagnosis_question = {
    "English": "Has a doctor or psychologist ever diagnosed you (or your child) with ADHD?",
    "العربية": "هل قام الطبيب أو الأخصائي النفسي بتشخيصك (أو تشخيص طفلك) باضطراب فرط الحركة وتشتت الانتباه؟",
    "Français": "Un médecin ou un psychologue a-t-il déjà diagnostiqué un TDAH chez vous (ou chez votre enfant)?"
}

diagnosis_options = {
    "English": ["Yes, diagnosed", "No, not diagnosed", "Not sure"],
    "العربية": ["نعم، تم التشخيص", "لا، لم يتم التشخيص", "لست متأكداً"],
    "Français": ["Oui, diagnostiqué", "Non, pas diagnostiqué", "Je ne suis pas sûr(e)"]
}

diagnosis = st.selectbox(diagnosis_question[language], diagnosis_options[language])

# -------------------------------
# 6. TRANSLATE ALL ANSWERS TO ENGLISH
# -------------------------------
translated_answers = [translate_to_english(ans) for ans in answers]
translated_comorbidity = [translate_to_english(ans) for ans in comorbidity_answers]
diagnosis_english = translate_to_english(diagnosis)

# -------------------------------
# 7. SAVE TO CSV
# -------------------------------
if st.button("Submit"):
    data = {
        "Name": [name],
        "Age": [age],
        "Gender": [gender],
        "Country": [country],
        "Patient_Type": [patient_type],
        "ADHD_Diagnosed": [diagnosis_english],
        **{f"Q{i+1}": [translated_answers[i]] for i in range(len(translated_answers))},
        **{f"Comorbidity_{i+1}": [translated_comorbidity[i]] for i in range(len(translated_comorbidity))},
        "Language": [language],
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    }

    df = pd.DataFrame(data)

    # Append to existing CSV or create new one
    if os.path.exists("adhd_responses.csv"):
        existing = pd.read_csv("adhd_responses.csv")
        df = pd.concat([existing, df], ignore_index=True)

    df.to_csv("adhd_responses.csv", index=False)
    st.success("✅ Your answers have been saved successfully!")
    st.info("All answers have been translated into English for AI processing.")
