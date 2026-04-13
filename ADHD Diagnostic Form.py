import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="ADHD Clinical Form", layout="centered")

st.markdown("""
<style>
html, body, [class*="css"] {
    direction: ltr;
    text-align: left;
}

.ar {
    direction: rtl !important;
    text-align: right !important;
}
</style>
""", unsafe_allow_html=True)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "ADHD_Responses"

# -------------------------
# GOOGLE SHEETS AUTH
# -------------------------
try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
except:
    st.error("Google Sheets access error")
    st.stop()

# -------------------------
# LANGUAGE
# -------------------------
lang_choice = st.selectbox(
    "Preferred language / اللغة / Langue",
    ["English", "Français", "العربية"]
)

lang_code = {"English": "en", "Français": "fr", "العربية": "ar"}[lang_choice]

def is_ar():
    return lang_code == "ar"

# -------------------------
# TRANSLATIONS
# -------------------------
T = {
    "title": {
        "en": "ADHD Clinical Questionnaire",
        "fr": "Questionnaire clinique du TDAH",
        "ar": "استبيان اضطراب فرط الحركة وتشتت الانتباه"
    },
    "intro": {
        "en": "This form collects clinical information used for ADHD assessment.",
        "fr": "Ce formulaire recueille des informations cliniques pour l’évaluation du TDAH.",
        "ar": "يجمع هذا النموذج معلومات سريرية لتقييم اضطراب فرط الحركة وتشتت الانتباه."
    },
    "participant": {
        "en": "Participant information",
        "fr": "Informations du participant",
        "ar": "معلومات المشارك"
    },
    "history": {
        "en": "History and context",
        "fr": "Antécédents et contexte",
        "ar": "التاريخ والسياق"
    },
    "dsm": {
        "en": "DSM-5 symptom checklist",
        "fr": "Liste DSM-5",
        "ar": "قائمة DSM-5"
    },
    "asrs": {
        "en": "ASRS screener",
        "fr": "ASRS",
        "ar": "مقياس ASRS"
    },
    "safety": {
        "en": "Safety",
        "fr": "Sécurité",
        "ar": "السلامة"
    },
    "eeg": {
        "en": "Do you agree to EEG test?",
        "fr": "Acceptez-vous un EEG ?",
        "ar": "هل توافق على اختبار EEG؟"
    },
    "consent": {
        "en": "I consent to data storage",
        "fr": "Je consens au stockage des données",
        "ar": "أوافق على تخزين البيانات"
    },
    "functional": {
        "en": "Functional impairment",
        "fr": "Impact fonctionnel",
        "ar": "التأثير الوظيفي"
    }
}

def t(k):
    return T[k][lang_code]

# -------------------------
# OPTIONS
# -------------------------
freq_options = {
    "en": ["", "Never", "Rarely", "Sometimes", "Often", "Very often"],
    "fr": ["", "Jamais", "Rarement", "Parfois", "Souvent", "Très souvent"],
    "ar": ["", "أبداً", "نادراً", "أحياناً", "غالباً", "كثيراً جداً"]
}

# -------------------------
# QUESTIONS
# -------------------------
SYMPTOMS = [
    {"en": "Fails to give attention", "fr": "Ne fait pas attention", "ar": "لا ينتبه"},
    {"en": "Difficulty sustaining attention", "fr": "Difficulté d'attention", "ar": "صعوبة التركيز"},
    {"en": "Does not listen", "fr": "N'écoute pas", "ar": "لا يستمع"},
]

asrs_items = [
    {"en": "Forget appointments", "fr": "Oublie les rendez-vous", "ar": "ينسى المواعيد"},
    {"en": "Difficulty finishing tasks", "fr": "Difficulté à terminer", "ar": "صعوبة إنهاء المهام"},
]

# -------------------------
# UI WRAPPER
# -------------------------
if is_ar():
    st.markdown('<div class="ar">', unsafe_allow_html=True)

st.title(t("title"))
st.write(t("intro"))

# -------------------------
# PARTICIPANT
# -------------------------
st.header(t("participant"))

participant_id = str(uuid.uuid4())

name = st.text_input("Full name / Nom / الاسم")
email = st.text_input("Email")
phone = st.text_input("Phone")
age = st.text_input("Age / DOB")

gender = st.selectbox("Gender", ["Male", "Female"])
responder = st.selectbox("Responder", ["Self", "Parent", "Teacher"])

# -------------------------
# DSM
# -------------------------
st.header(t("dsm"))
sym_answers = {}

for i, s in enumerate(SYMPTOMS, 1):
    sym_answers[f"Symptom_{i}"] = st.selectbox(
        f"{i}. {s[lang_code]}",
        freq_options[lang_code]
    )

# -------------------------
# ASRS
# -------------------------
st.header(t("asrs"))
asrs_answers = {}

for i, q in enumerate(asrs_items, 1):
    asrs_answers[f"ASRS_{i}"] = st.selectbox(
        f"{i}. {q[lang_code]}",
        freq_options[lang_code]
    )

# -------------------------
# HISTORY
# -------------------------
st.header(t("history"))

functional_impairment = st.text_area(t("functional"))

multi_setting = st.selectbox(
    "Multiple settings?",
    ["", "Yes", "No"] if not is_ar() else ["", "نعم", "لا"]
)

# -------------------------
# SAFETY
# -------------------------
st.header(t("safety"))

suicidality = st.selectbox(
    "Self-harm thoughts?" if not is_ar() else "أفكار إيذاء النفس؟",
    ["", "No", "Passive", "Active"] if not is_ar()
    else ["", "لا", "أفكار غير مباشرة", "نشطة"]
)

# -------------------------
# EEG
# -------------------------
eeg_consent = st.selectbox(
    t("eeg"),
    ["Yes", "No"] if not is_ar() else ["نعم", "لا"]
)

# -------------------------
# CONSENT
# -------------------------
consent = st.checkbox(t("consent"))

if is_ar():
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# SUBMIT
# -------------------------
if st.button("Submit"):

    if not consent:
        st.error("Consent required")
    else:
        row = [
            participant_id,
            name,
            email,
            phone,
            age,
            gender,
            responder,
            lang_choice
        ]

        row += list(sym_answers.values())
        row += list(asrs_answers.values())

        row += [
            functional_impairment,
            multi_setting,
            suicidality,
            eeg_consent,
            "Yes",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        try:
            sheet.append_row(row)
            st.success("Saved successfully")
        except Exception as e:
            st.error(f"Error: {e}")
