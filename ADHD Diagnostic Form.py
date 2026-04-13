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

# -------------------------
# TRANSLATIONS (NO AUTO TRANSLATION)
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
        "en": "Participant and responder information",
        "fr": "Informations du participant",
        "ar": "معلومات المشارك"
    },
    "history": {
        "en": "History and context",
        "fr": "Antécédents et contexte",
        "ar": "التاريخ والسياق"
    },
    "dsm": {
        "en": "DSM-5 ADHD symptom checklist — frequency in last 6 months",
        "fr": "Liste des symptômes TDAH DSM-5 — fréquence (6 derniers mois)",
        "ar": "قائمة أعراض DSM-5 — خلال آخر 6 أشهر"
    },
    "asrs": {
        "en": "ASRS-6 screener (brief adult items)",
        "fr": "ASRS-6 (dépistage adulte)",
        "ar": "مقياس ASRS-6"
    },
    "safety": {
        "en": "Safety",
        "fr": "Sécurité",
        "ar": "السلامة"
    },
    "consent": {
        "en": "I consent to storing my data for clinical purposes.",
        "fr": "Je consens au stockage de mes données à des fins cliniques.",
        "ar": "أوافق على تخزين بياناتي لأغراض سريرية."
    },
    "eeg": {
        "en": "Do you agree to participate in an EEG test?",
        "fr": "Acceptez-vous de participer à un test EEG ?",
        "ar": "هل توافق على إجراء اختبار EEG؟"
    }
}

def t(k):
    return T[k][lang_code]

# -------------------------
# OPTIONS (FREQUENCY - FIXED TRANSLATION)
# -------------------------
freq_options = {
    "en": ["", "Never", "Rarely", "Sometimes", "Often", "Very often"],
    "fr": ["", "Jamais", "Rarement", "Parfois", "Souvent", "Très souvent"],
    "ar": ["", "أبداً", "نادراً", "أحياناً", "غالباً", "كثيراً جداً"]
}

# -------------------------
# EEG OPTIONS (NEW - TRANSLATED)
# -------------------------
eeg_options = {
    "en": ["Yes", "No"],
    "fr": ["Oui", "Non"],
    "ar": ["نعم", "لا"]
}

# -------------------------
# DSM-5 QUESTIONS
# -------------------------
SYMPTOMS = [
    {"en": "Fails to give close attention to details or makes careless mistakes",
     "fr": "Ne prête pas attention aux détails ou fait des erreurs d’inattention",
     "ar": "لا ينتبه للتفاصيل أو يرتكب أخطاء بسبب الإهمال"},
    {"en": "Has difficulty sustaining attention in tasks or play",
     "fr": "A des difficultés à maintenir son attention",
     "ar": "يواجه صعوبة في الحفاظ على الانتباه"},
    {"en": "Does not seem to listen when spoken to directly",
     "fr": "Semble ne pas écouter lorsqu’on lui parle directement",
     "ar": "يبدو وكأنه لا يستمع عند التحدث إليه مباشرة"},
    {"en": "Does not follow through on instructions or finish tasks",
     "fr": "Ne suit pas les instructions ou ne termine pas les tâches",
     "ar": "لا يتبع التعليمات أو لا يكمل المهام"},
    {"en": "Has difficulty organizing tasks and activities",
     "fr": "A des difficultés à organiser les tâches",
     "ar": "يواجه صعوبة في تنظيم المهام"},
    {"en": "Avoids tasks requiring sustained mental effort",
     "fr": "Évite les tâches nécessitant un effort mental",
     "ar": "يتجنب المهام التي تتطلب جهداً ذهنياً"},
    {"en": "Loses things necessary for tasks or activities",
     "fr": "Perd des objets nécessaires",
     "ar": "يفقد الأشياء الضرورية"},
    {"en": "Is easily distracted",
     "fr": "Facilement distrait",
     "ar": "يتشتت بسهولة"},
    {"en": "Is often forgetful in daily activities",
     "fr": "Oublis fréquents",
     "ar": "كثير النسيان"},
    {"en": "Fidgets or taps hands or feet",
     "fr": "Remue les mains ou pieds",
     "ar": "يتململ أو يحرك يديه أو قدميه"},
    {"en": "Leaves seat when remaining seated is expected",
     "fr": "Se lève alors qu’il doit rester assis",
     "ar": "يغادر مكانه عندما يجب أن يبقى جالساً"},
    {"en": "Runs or climbs excessively",
     "fr": "Court ou grimpe excessivement",
     "ar": "يركض أو يتسلق بشكل مفرط"},
    {"en": "Difficulty playing quietly",
     "fr": "Difficulté à jouer calmement",
     "ar": "صعوبة في اللعب بهدوء"},
    {"en": "Is often 'on the go'",
     "fr": "Toujours en mouvement",
     "ar": "دائم الحركة"},
    {"en": "Talks excessively",
     "fr": "Parle excessivement",
     "ar": "يتحدث كثيراً"},
    {"en": "Blurts out answers before questions are completed",
     "fr": "Répond avant la fin",
     "ar": "يجيب قبل انتهاء السؤال"},
    {"en": "Has difficulty waiting turn",
     "fr": "Difficulté à attendre son tour",
     "ar": "صعوبة في انتظار الدور"},
    {"en": "Interrupts or intrudes on others",
     "fr": "Interrompt les autres",
     "ar": "يقاطع الآخرين"}
]

# -------------------------
# ASRS
# -------------------------
asrs_items = [
    {"en": "How often do you forget appointments or obligations?",
     "fr": "À quelle fréquence oubliez-vous vos rendez-vous ?",
     "ar": "كم مرة تنسى المواعيد؟"},
    {"en": "How often do you have difficulty finishing tasks?",
     "fr": "À quelle fréquence avez-vous du mal à terminer les tâches ?",
     "ar": "كم مرة تواجه صعوبة في إنهاء المهام؟"},
    {"en": "How often do you have difficulty concentrating when spoken to?",
     "fr": "À quelle fréquence avez-vous des difficultés à vous concentrer lorsqu’on vous parle ?",
     "ar": "كم مرة تواجه صعوبة في التركيز عند التحدث إليك؟"}
]

# -------------------------
# UI
# -------------------------
st.title(t("title"))
st.write(t("intro"))

st.header(t("participant"))

participant_id = str(uuid.uuid4())
name = st.text_input("Full name / Nom / الاسم الكامل")
email = st.text_input("Email / البريد الإلكتروني")
phone = st.text_input("Phone / الهاتف")
dob_or_age = st.text_input("Age / Date of birth")

gender = st.selectbox("Gender", ["Male", "Female"])
responder = st.selectbox("Responder", ["Self", "Parent", "Teacher"])

st.header(t("dsm"))

sym_answers = {}
for i, s in enumerate(SYMPTOMS, 1):
    sym_answers[f"Symptom_{i}"] = st.selectbox(
        f"{i}. {s[lang_code]}",
        freq_options[lang_code]
    )

st.header(t("asrs"))

asrs_answers = {}
for i, q in enumerate(asrs_items, 1):
    asrs_answers[f"ASRS_{i}"] = st.selectbox(
        f"{i}. {q[lang_code]}",
        freq_options[lang_code]
    )

st.header(t("history"))

functional_impairment = st.text_area("Functional impairment / impact")
multi_setting = st.selectbox("Symptoms in multiple settings?", ["", "Yes", "No"])

st.header(t("safety"))

suicidality = st.selectbox(
    "Self-harm thoughts?",
    ["", "No", "Passive", "Active"]
)

# -------------------------
# EEG QUESTION (NOW TRANSLATED)
# -------------------------
eeg_consent = st.selectbox(
    t("eeg"),
    eeg_options[lang_code]
)

consent = st.checkbox(t("consent"))

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
            dob_or_age,
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
            "Yes" if consent else "No",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        try:
            sheet.append_row(row)
            st.success("Saved successfully")
        except Exception as e:
            st.error(f"Error: {e}")
