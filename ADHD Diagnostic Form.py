import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid
from deep_translator import GoogleTranslator

# ===============================
# GOOGLE SHEETS SETUP
# ===============================
SERVICE_ACCOUNT = st.secrets["google_service_account"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open("ADHD_Responses").sheet1
except Exception as e:
    st.warning("Google Sheets access error. Make sure API is enabled and sheet is shared with service account.")
    st.stop()

# ===============================
# APP TITLE
# ===============================
st.title("ADHD Diagnostic Form")

# ===============================
# LANGUAGE SELECTION
# ===============================
language = st.selectbox("Preferred Language / اللغة المفضلة / Langue préférée", ["English", "العربية", "Français"])

def translate(text):
    if language == "English":
        return text
    return GoogleTranslator(source="en", target=language.lower()).translate(text)

# ===============================
# PARTICIPANT INFORMATION
# ===============================
st.header(translate("Participant Information"))
participant_id = str(uuid.uuid4())
name = st.text_input(translate("Full Name"))
email = st.text_input(translate("Email Address"))
phone = st.text_input(translate("Phone Number"))
age = st.number_input(translate("Age"), min_value=3, max_value=100, step=1)
gender = st.selectbox(translate("Gender"), [translate("Male"), translate("Female")])
patient_type = st.radio(translate("Are you filling this for a child or adult?"), [translate("Child"), translate("Adult")])

# ===============================
# ADHD QUESTIONS
# ===============================
st.header(translate("ADHD Symptoms Questions"))
st.write(translate("Please answer all questions. All questions are mandatory."))

symptoms = [
    "Often fails to give close attention to details or makes careless mistakes in schoolwork, work, or other activities.",
    "Often has difficulty sustaining attention in tasks or play activities.",
    "Often does not seem to listen when spoken to directly.",
    "Often does not follow through on instructions and fails to finish schoolwork, chores, or duties.",
    "Often has difficulty organizing tasks and activities.",
    "Often avoids, dislikes, or is reluctant to engage in tasks that require sustained mental effort.",
    "Often loses things necessary for tasks or activities.",
    "Is often easily distracted by extraneous stimuli.",
    "Is often forgetful in daily activities.",
    "Often fidgets with or taps hands or feet or squirms in seat.",
    "Often leaves seat in situations when remaining seated is expected.",
    "Often runs about or climbs in situations where it is inappropriate.",
    "Often unable to play or engage in leisure activities quietly.",
    "Is often 'on the go' or acts as if 'driven by a motor'.",
    "Often talks excessively.",
    "Often blurts out answers before questions have been completed.",
    "Often has difficulty waiting his or her turn.",
    "Often interrupts or intrudes on others (e.g., butts into conversations or games)."
]

answers = {}
for i, q in enumerate(symptoms, 1):
    prefix = translate("Does your child") if patient_type == translate("Child") else translate("Do you")
    full_question = f"{prefix} {translate(q)}"
    answers[f"Symptom_{i}"] = st.selectbox(
        f"{i}. {full_question}",
        ["", translate("Never"), translate("Rarely"), translate("Sometimes"), translate("Often"), translate("Very Often")],
        key=f"q{i}"
    )

# ===============================
# COMORBIDITIES
# ===============================
st.header(translate("Comorbidities / Associated Conditions"))
comorbidities = [
    "Anxiety or excessive worry",
    "Depression or persistent sadness",
    "Oppositional defiant behavior",
    "Learning difficulties or dyslexia"
]

comorbidity_answers = {}
for i, q in enumerate(comorbidities, 1):
    comorbidity_answers[f"Comorbidity_{i}"] = st.selectbox(
        f"{translate(q)}?",
        ["", translate("No"), translate("Yes")], key=f"c{i}"
    )

# ===============================
# CHILDHOOD HISTORY & FUNCTIONAL IMPAIRMENT
# ===============================
childhood_history = ""
if patient_type == translate("Adult"):
    st.header(translate("Childhood History"))
    childhood_history = st.text_area(translate("Did you show ADHD symptoms during childhood? Describe if known."))

st.header(translate("Functional Impairment"))
functional_impairment = st.text_area(translate("Do these symptoms cause significant impairment in social, academic, or occupational functioning?"))

multi_setting = st.radio(
    translate("Are these symptoms observed in more than one setting (e.g., home, school, work)?"),
    ["", translate("Yes"), translate("No")]
)

# Parent/guardian role
st.header(translate("Parent / Guardian Role (if child)"))
parent_role = ""
if patient_type == translate("Child"):
    parent_role = st.text_input(translate("Please indicate your relationship to the child (e.g., mother, father, guardian)"))

# ===============================
# SUBMISSION
# ===============================
if st.button(translate("Submit")):
    mandatory_filled = all(v != "" for v in answers.values()) \
                       and all(v != "" for v in comorbidity_answers.values()) \
                       and name != "" and email != "" and phone != "" and age != "" and gender != "" \
                       and functional_impairment != "" and multi_setting != ""

    if patient_type == translate("Adult"):
        mandatory_filled = mandatory_filled and childhood_history != ""
    if patient_type == translate("Child"):
        mandatory_filled = mandatory_filled and parent_role != ""

    if not mandatory_filled:
        st.error(translate("Please answer all mandatory questions before submitting."))
    else:
        row = [
            participant_id, name, email, phone, age, gender, patient_type, language,
            childhood_history if patient_type == translate("Adult") else "",
            parent_role if patient_type == translate("Child") else "",
            functional_impairment, multi_setting, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        row.extend(answers.values())
        row.extend(comorbidity_answers.values())
        try:
            sheet.append_row(row)
            st.success(translate("Your responses have been submitted successfully. All information is private."))
        except Exception as e:
            st.error(f"{translate('Error submitting to Google Sheet')}: {e}")
