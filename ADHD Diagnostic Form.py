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
# ANSWER OPTIONS (TRANSLATED)
# -------------------------
OPTIONS = {
    "en": ["", "Never", "Rarely", "Sometimes", "Often", "Very often"],
    "fr": ["", "Jamais", "Rarement", "Parfois", "Souvent", "Très souvent"],
    "ar": ["", "أبداً", "نادراً", "أحياناً", "غالباً", "كثيراً جداً"]
}

# -------------------------
# TEXT TRANSLATIONS
# -------------------------
TEXT = {
    "title": {
        "en": "ADHD Clinical Questionnaire",
        "fr": "Questionnaire clinique du TDAH",
        "ar": "استبيان اضطراب فرط الحركة وتشتت الانتباه"
    },
    "intro": {
        "en": "Please answer the following questions based on behavior during the last 6 months.",
        "fr": "Veuillez répondre aux questions suivantes en vous basant sur les 6 derniers mois.",
        "ar": "يرجى الإجابة على الأسئلة التالية بناءً على السلوك خلال الأشهر الستة الماضية."
    },
    "submit": {"en": "Submit", "fr": "Soumettre", "ar": "إرسال"},
    "consent": {
        "en": "I consent to data collection for clinical/research purposes",
        "fr": "Je consens à la collecte des données à des fins cliniques/recherche",
        "ar": "أوافق على جمع البيانات لأغراض سريرية/بحثية"
    }
}

def t(key):
    return TEXT[key][lang_code]

# -------------------------
# DSM QUESTIONS (FULL TRANSLATION)
# -------------------------
QUESTIONS = [
    {
        "en": "How often do you make careless mistakes in school, work, or other activities?",
        "fr": "À quelle fréquence faites-vous des erreurs d’inattention dans votre travail ou vos activités ?",
        "ar": "كم مرة ترتكب أخطاء بسبب الإهمال في العمل أو الدراسة أو الأنشطة الأخرى؟"
    },
    {
        "en": "How often do you have difficulty sustaining attention?",
        "fr": "À quelle fréquence avez-vous des difficultés à maintenir votre attention ?",
        "ar": "كم مرة تواجه صعوبة في الحفاظ على الانتباه؟"
    },
    {
        "en": "How often do you seem not to listen when spoken to directly?",
        "fr": "À quelle fréquence semblez-vous ne pas écouter lorsqu’on vous parle directement ؟",
        "ar": "كم مرة يبدو أنك لا تستمع عند التحدث إليك مباشرة؟"
    },
    {
        "en": "How often do you fail to complete tasks?",
        "fr": "À quelle fréquence ne terminez-vous pas vos tâches ؟",
        "ar": "كم مرة لا تكمل المهام المطلوبة منك؟"
    },
    {
        "en": "How often do you have difficulty organizing tasks?",
        "fr": "À quelle fréquence avez-vous des difficultés à organiser vos tâches ؟",
        "ar": "كم مرة تواجه صعوبة في تنظيم المهام؟"
    },
    {
        "en": "How often do you avoid tasks requiring mental effort?",
        "fr": "À quelle fréquence évitez-vous les tâches nécessitant un effort mental ؟",
        "ar": "كم مرة تتجنب المهام التي تتطلب جهداً ذهنياً؟"
    },
    {
        "en": "How often do you lose important items?",
        "fr": "À quelle fréquence perdez-vous des objets importants ؟",
        "ar": "كم مرة تفقد أشياء مهمة؟"
    },
    {
        "en": "How often are you easily distracted?",
        "fr": "À quelle fréquence êtes-vous facilement distrait ؟",
        "ar": "كم مرة تتشتت بسهولة؟"
    },
    {
        "en": "How often are you forgetful in daily activities?",
        "fr": "À quelle fréquence oubliez-vous des activités quotidiennes ؟",
        "ar": "كم مرة تنسى الأنشطة اليومية؟"
    },
    {
        "en": "How often do you fidget or move excessively?",
        "fr": "À quelle fréquence bougez-vous de manière excessive ؟",
        "ar": "كم مرة تتحرك أو تتململ بشكل مفرط؟"
    },
    {
        "en": "How often do you leave your seat when expected to stay seated?",
        "fr": "À quelle fréquence vous levez-vous alors que vous devez rester assis ؟",
        "ar": "كم مرة تغادر مكانك عندما يُطلب منك البقاء جالساً؟"
    },
    {
        "en": "How often do you feel restless?",
        "fr": "À quelle fréquence vous sentez-vous agité ؟",
        "ar": "كم مرة تشعر بعدم الهدوء؟"
    },
    {
        "en": "How often do you have difficulty engaging in quiet activities?",
        "fr": "À quelle fréquence avez-vous des difficultés à rester calme ؟",
        "ar": "كم مرة تواجه صعوبة في القيام بأنشطة بهدوء؟"
    },
    {
        "en": "How often do you feel constantly active?",
        "fr": "À quelle fréquence êtes-vous constamment actif ؟",
        "ar": "كم مرة تشعر أنك دائم الحركة؟"
    },
    {
        "en": "How often do you talk excessively?",
        "fr": "À quelle fréquence parlez-vous de façon excessive ؟",
        "ar": "كم مرة تتحدث بشكل مفرط؟"
    },
    {
        "en": "How often do you interrupt others?",
        "fr": "À quelle fréquence interrompez-vous les autres ؟",
        "ar": "كم مرة تقاطع الآخرين؟"
    },
    {
        "en": "How often do you have difficulty waiting your turn?",
        "fr": "À quelle fréquence avez-vous du mal à attendre votre tour ؟",
        "ar": "كم مرة تواجه صعوبة في انتظار دورك؟"
    },
    {
        "en": "How often do you answer before a question is completed?",
        "fr": "À quelle fréquence répondez-vous avant la fin de la question ؟",
        "ar": "كم مرة تجيب قبل انتهاء السؤال؟"
    }
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

consent = st.checkbox(t("consent"))

# -------------------------
# SUBMIT
# -------------------------
if st.button(t("submit")):

    if not consent or "" in answers.values():
        st.error("Please complete all questions")
    else:
        row = [str(uuid.uuid4()), lang_choice]
        row += list(answers.values())
        row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            sheet.append_row(row)
            st.success("Submission successful")
        except:
            st.error("Error saving data")
