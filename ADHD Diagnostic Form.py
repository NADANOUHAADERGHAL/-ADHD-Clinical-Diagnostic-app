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
T = {
    "title": {
        "en": "ADHD Clinical Questionnaire",
        "fr": "Questionnaire clinique du TDAH",
        "ar": "استبيان اضطراب فرط الحركة وتشتت الانتباه"
    },
    "intro": {
        "en": "This form collects clinical information for ADHD assessment.",
        "fr": "Ce formulaire recueille des informations cliniques pour l’évaluation du TDAH.",
        "ar": "يجمع هذا النموذج معلومات سريرية لتقييم اضطراب فرط الحركة وتشتت الانتباه."
    },
    "name": {"en": "Full name", "fr": "Nom complet", "ar": "الاسم الكامل"},
    "email": {"en": "Email", "fr": "Email", "ar": "البريد الإلكتروني"},
    "phone": {"en": "Phone number", "fr": "Numéro de téléphone", "ar": "رقم الهاتف"},
    "dob": {"en": "Age or date of birth", "fr": "Âge ou date de naissance", "ar": "العمر أو تاريخ الميلاد"},
    "gender": {"en": "Gender", "fr": "Sexe", "ar": "الجنس"},
    "male": {"en": "Male", "fr": "Homme", "ar": "ذكر"},
    "female": {"en": "Female", "fr": "Femme", "ar": "أنثى"},
    "submit": {"en": "Submit", "fr": "Soumettre", "ar": "إرسال"},
    "consent": {
        "en": "I consent to data collection",
        "fr": "Je consens à la collecte des données",
        "ar": "أوافق على جمع البيانات"
    }
}

def t(key):
    return T.get(key, {}).get(lang_code, key)

# -------------------------
# DSM SYMPTOMS
# -------------------------
SYMPTOMS = [
    {
        "en": "Fails to give close attention to details or makes careless mistakes",
        "fr": "Ne prête pas attention aux détails ou fait des erreurs d’inattention",
        "ar": "لا ينتبه للتفاصيل أو يرتكب أخطاء بسبب الإهمال"
    },
    {
        "en": "Has difficulty sustaining attention in tasks or play",
        "fr": "A des difficultés à maintenir son attention",
        "ar": "يواجه صعوبة في الحفاظ على الانتباه"
    },
    {
        "en": "Does not seem to listen when spoken to directly",
        "fr": "Semble ne pas écouter lorsqu’on lui parle directement",
        "ar": "يبدو وكأنه لا يستمع عند التحدث إليه مباشرة"
    },
    {
        "en": "Does not follow instructions or finish tasks",
        "fr": "Ne suit pas les instructions ou ne termine pas les tâches",
        "ar": "لا يتبع التعليمات أو لا يكمل المهام"
    },
    {
        "en": "Has difficulty organizing tasks",
        "fr": "A des difficultés à organiser les tâches",
        "ar": "يواجه صعوبة في تنظيم المهام"
    },
    {
        "en": "Avoids tasks requiring sustained effort",
        "fr": "Évite les tâches nécessitant un effort mental soutenu",
        "ar": "يتجنب المهام التي تتطلب جهداً ذهنياً مستمراً"
    },
    {
        "en": "Loses necessary items",
        "fr": "Perd les objets nécessaires",
        "ar": "يفقد الأشياء الضرورية"
    },
    {
        "en": "Easily distracted",
        "fr": "Facilement distrait",
        "ar": "يتشتت بسهولة"
    },
    {
        "en": "Forgetful in daily activities",
        "fr": "Oublis fréquents dans les activités quotidiennes",
        "ar": "كثير النسيان في الأنشطة اليومية"
    },
    {
        "en": "Fidgets or squirms",
        "fr": "Remue souvent",
        "ar": "كثير الحركة أو يتململ"
    },
    {
        "en": "Leaves seat when expected to stay seated",
        "fr": "Se lève souvent alors qu’il devrait rester assis",
        "ar": "يغادر مكانه عندما يُتوقع منه البقاء جالساً"
    },
    {
        "en": "Runs or climbs excessively",
        "fr": "Court ou grimpe de façon excessive",
        "ar": "يركض أو يتسلق بشكل مفرط"
    },
    {
        "en": "Difficulty playing quietly",
        "fr": "Difficulté à jouer calmement",
        "ar": "صعوبة في اللعب بهدوء"
    },
    {
        "en": "Always 'on the go'",
        "fr": "Toujours en mouvement",
        "ar": "دائم الحركة"
    },
    {
        "en": "Talks excessively",
        "fr": "Parle excessivement",
        "ar": "يتحدث كثيراً"
    },
    {
        "en": "Blurts out answers",
        "fr": "Répond avant la fin des questions",
        "ar": "يجيب قبل انتهاء السؤال"
    },
    {
        "en": "Difficulty waiting turn",
        "fr": "Difficulté à attendre son tour",
        "ar": "صعوبة في انتظار الدور"
    },
    {
        "en": "Interrupts others",
        "fr": "Interrompt les autres",
        "ar": "يقاطع الآخرين"
    }
]

# -------------------------
# UI
# -------------------------
st.title(t("title"))
st.write(t("intro"))

name = st.text_input(t("name"))
email = st.text_input(t("email"))
phone = st.text_input(t("phone"))
dob = st.text_input(t("dob"))

gender = st.selectbox(
    t("gender"),
    [t("male"), t("female")]
)

# DSM Section
st.header("DSM-5")

options = ["", "Never", "Rarely", "Sometimes", "Often", "Very often"]

answers = {}
for i, s in enumerate(SYMPTOMS, 1):
    q = s[lang_code]
    answers[f"Symptom_{i}"] = st.selectbox(f"{i}. {q}", options)

# Consent
consent = st.checkbox(t("consent"))

# -------------------------
# SUBMIT
# -------------------------
if st.button(t("submit")):

    if not name or not email or not phone or not consent:
        st.error("Missing required fields")
    else:
        row = [
            str(uuid.uuid4()),
            name, email, phone, dob, gender, lang_choice
        ]

        row += list(answers.values())
        row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            sheet.append_row(row)
            st.success("Submitted successfully")
        except:
            st.error("Error saving data")
