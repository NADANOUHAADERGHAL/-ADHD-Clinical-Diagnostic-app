import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="ADHD Clinical Form", layout="centered")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "ADHD_Responses"

# -------------------------
# GOOGLE SHEETS
# -------------------------
try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
except:
    st.error("Google Sheets connection error")
    st.stop()

# -------------------------
# LANGUAGE
# -------------------------
lang_choice = st.selectbox(
    "Language / اللغة / Langue",
    ["English", "Français", "العربية"]
)

lang_code = {"English": "en", "Français": "fr", "العربية": "ar"}[lang_choice]

# -------------------------
# TRANSLATIONS
# -------------------------
TEXT = {
    "title": {
        "en": "ADHD Clinical Questionnaire",
        "fr": "Questionnaire clinique du TDAH",
        "ar": "استبيان اضطراب فرط الحركة وتشتت الانتباه"
    },
    "intro": {
        "en": "Please answer based on behavior over the last 6 months.",
        "fr": "Veuillez répondre selon le comportement خلال les 6 derniers mois.",
        "ar": "يرجى الإجابة بناءً على السلوك خلال الأشهر الستة الماضية."
    },
    "submit": {"en": "Submit", "fr": "Soumettre", "ar": "إرسال"},
    "consent": {
        "en": "I consent to data collection for research purposes",
        "fr": "Je consens à la collecte des données pour la recherche",
        "ar": "أوافق على جمع البيانات لأغراض البحث"
    },
    "eeg": {
        "en": "Do you agree to participate in an EEG test?",
        "fr": "Acceptez-vous de participer à un test EEG ?",
        "ar": "هل توافق على المشاركة في اختبار تخطيط الدماغ (EEG)؟"
    },
    "yes": {"en": "Yes", "fr": "Oui", "ar": "نعم"},
    "no": {"en": "No", "fr": "Non", "ar": "لا"}
}

def t(key):
    return TEXT[key][lang_code]

# -------------------------
# ANSWER OPTIONS
# -------------------------
OPTIONS = {
    "en": ["", "Never", "Rarely", "Sometimes", "Often", "Very often"],
    "fr": ["", "Jamais", "Rarement", "Parfois", "Souvent", "Très souvent"],
    "ar": ["", "أبداً", "نادراً", "أحياناً", "غالباً", "كثيراً جداً"]
}

YES_NO = {
    "en": [t("yes"), t("no")],
    "fr": [t("yes"), t("no")],
    "ar": [t("yes"), t("no")]
}

# -------------------------
# DSM QUESTIONS (18 FULL)
# -------------------------
QUESTIONS = [
    {"en": "Fails to give close attention to details or makes careless mistakes",
     "fr": "Ne prête pas attention aux détails ou fait des erreurs d’inattention",
     "ar": "لا ينتبه للتفاصيل أو يرتكب أخطاء بسبب الإهمال"},

    {"en": "Has difficulty sustaining attention",
     "fr": "A des difficultés à maintenir son attention",
     "ar": "يواجه صعوبة في الحفاظ على الانتباه"},

    {"en": "Does not seem to listen when spoken to directly",
     "fr": "Semble ne pas écouter lorsqu’on lui parle",
     "ar": "يبدو وكأنه لا يستمع عند التحدث إليه"},

    {"en": "Does not follow instructions or finish tasks",
     "fr": "Ne suit pas les instructions ou ne termine pas les tâches",
     "ar": "لا يتبع التعليمات أو لا يكمل المهام"},

    {"en": "Difficulty organizing tasks",
     "fr": "Difficulté à organiser les tâches",
     "ar": "صعوبة في تنظيم المهام"},

    {"en": "Avoids tasks requiring mental effort",
     "fr": "Évite les tâches nécessitant un effort mental",
     "ar": "يتجنب المهام التي تتطلب جهداً ذهنياً"},

    {"en": "Loses necessary items",
     "fr": "Perd des objets nécessaires",
     "ar": "يفقد الأشياء الضرورية"},

    {"en": "Easily distracted",
     "fr": "Facilement distrait",
     "ar": "يتشتت بسهولة"},

    {"en": "Forgetful in daily activities",
     "fr": "Oublis fréquents",
     "ar": "كثير النسيان"},

    {"en": "Fidgets or moves excessively",
     "fr": "Bouge excessivement",
     "ar": "يتحرك بشكل مفرط"},

    {"en": "Leaves seat when expected to stay seated",
     "fr": "Se lève lorsqu’il doit rester assis",
     "ar": "يغادر مكانه عندما يجب أن يبقى جالساً"},

    {"en": "Runs or climbs excessively",
     "fr": "Court ou grimpe excessivement",
     "ar": "يركض أو يتسلق بشكل مفرط"},

    {"en": "Difficulty playing quietly",
     "fr": "Difficulté à jouer calmement",
     "ar": "صعوبة في اللعب بهدوء"},

    {"en": "Always on the go",
     "fr": "Toujours en mouvement",
     "ar": "دائم الحركة"},

    {"en": "Talks excessively",
     "fr": "Parle excessivement",
     "ar": "يتحدث كثيراً"},

    {"en": "Blurts out answers",
     "fr": "Répond avant la fin",
     "ar": "يجيب قبل انتهاء السؤال"},

    {"en": "Difficulty waiting turn",
     "fr": "Difficulté à attendre son tour",
     "ar": "صعوبة في انتظار الدور"},

    {"en": "Interrupts others",
     "fr": "Interrompt les autres",
     "ar": "يقاطع الآخرين"}
]

# -------------------------
# UI
# -------------------------
st.title(t("title"))
st.write(t("intro"))

answers = {}

for i, q in enumerate(QUESTIONS, 1):
    answers[f"Q{i}"] = st.selectbox(
        f"{i}. {q[lang_code]}",
        OPTIONS[lang_code]
    )

# EEG QUESTION
eeg_consent = st.selectbox(
    t("eeg"),
    YES_NO[lang_code]
)

# DATA CONSENT
consent = st.checkbox(t("consent"))

# -------------------------
# SUBMIT
# -------------------------
if st.button(t("submit")):

    if "" in answers.values() or not consent:
        st.error("Please complete all fields")
    else:
        row = [
            str(uuid.uuid4()),
            lang_choice
        ]

        row += list(answers.values())
        row.append(eeg_consent)
        row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            sheet.append_row(row)
            st.success("Submission successful")
        except:
            st.error("Error saving data")
