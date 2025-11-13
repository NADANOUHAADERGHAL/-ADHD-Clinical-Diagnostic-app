# app.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid

# optional translator; graceful fallback if not available or offline
try:
    from deep_translator import GoogleTranslator
    def translate_to(lang_code, text):
        if lang_code == "en": return text
        try:
            return GoogleTranslator(source="auto", target=lang_code).translate(text)
        except Exception:
            return text
except Exception:
    def translate_to(lang_code, text):
        return text

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="ADHD Clinical Form", layout="centered")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "ADHD_Responses"    # change if your sheet has another name

# -------------------------
# Authenticate to Google Sheets from Streamlit secrets
# (Make sure .streamlit/secrets.toml has [gcp_service_account] block)
# -------------------------
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    st.error("Google Sheets access error. Make sure APIs are enabled and the sheet is shared with your service account.")
    st.stop()

# -------------------------
# LANGUAGE
# -------------------------
lang_choice = st.selectbox("Preferred language / اللغة / Langue", ["English", "العربية", "Français"])
lang_code = {"English": "en", "العربية": "ar", "Français": "fr"}[lang_choice]

def t(s): return translate_to(lang_code, s)

# -------------------------
# Title & instructions
# -------------------------
st.title(t("ADHD Clinical Questionnaire"))
st.write(t("This form collects clinical information used for ADHD assessment. All data will be stored privately."))

# -------------------------
# Participant & responder info
# -------------------------
st.header(t("Participant and responder information"))
participant_id = str(uuid.uuid4())
name = st.text_input(t("Full name"))
email = st.text_input(t("Email"))
phone = st.text_input(t("Phone number"))
dob_or_age = st.text_input(t("Date of birth or age"))
gender = st.selectbox(t("Gender"), [t("Male"), t("Female"), t("Other")])
responder = st.selectbox(t("Who is answering?"), [t("Self (adult)"), t("Parent / guardian (for a child)"), t("Teacher / other")])

# -------------------------
# DSM-5 18 symptoms (frequency scale)
# -------------------------
st.header(t("DSM-5 ADHD symptom checklist — frequency in last 6 months"))
freq_options = ["", t("Never"), t("Rarely"), t("Sometimes"), t("Often"), t("Very often")]

symptom_texts = [
    # inattention 1-9
    "Fails to give close attention to details or makes careless mistakes",
    "Has difficulty sustaining attention in tasks or play",
    "Does not seem to listen when spoken to directly",
    "Does not follow through on instructions or finish tasks",
    "Has difficulty organizing tasks and activities",
    "Avoids or is reluctant to engage in tasks requiring sustained mental effort",
    "Loses things necessary for tasks or activities",
    "Is easily distracted by extraneous stimuli",
    "Is often forgetful in daily activities",
    # hyperactivity/impulsivity 10-18
    "Fidgets with or taps hands or feet; squirms in seat",
    "Often leaves seat when remaining seated is expected",
    "Runs about or climbs in situations where inappropriate (adults: extreme restlessness)",
    "Unable to play or engage in activities quietly",
    "Is often 'on the go' or acts as if 'driven by a motor'",
    "Talks excessively",
    "Blurts out answers before questions are completed",
    "Has difficulty waiting turn",
    "Interrupts or intrudes on others"
]

sym_answers = {}
for i, s in enumerate(symptom_texts, start=1):
    prefix = t("Does your child") if responder == t("Parent / guardian (for a child)") else (t("Does the person") if responder==t("Teacher / other") else t("Do you"))
    label = f"{i}. {prefix} {t(s)}?"
    sym_answers[f"Symptom_{i}"] = st.selectbox(label, freq_options, key=f"sym_{i}")

# optional: examples for clinicians
st.subheader(t("If possible, give one short example of typical problematic behaviour"))
sym_examples = st.text_area(t("Examples (optional)"))

# -------------------------
# Clinical history & context
# -------------------------
st.header(t("History and context"))
age_of_onset = st.text_input(t("Approximate age when symptoms were first noticed (e.g., 7)"))
onset_before_12 = st.selectbox(t("Were symptoms present before age 12?"), ["", t("Yes"), t("No")])
duration_months = st.text_input(t("Duration of problems (months or years)"))
multi_setting = st.selectbox(t("Are symptoms observed in more than one setting (home, school, work)?"), ["", t("Yes"), t("No")])
functional_impairment = st.text_area(t("Describe how symptoms impair daily functioning (social/academic/occupational)"))

prior_diagnosis = st.selectbox(t("Previous ADHD diagnosis?"), ["", t("Yes"), t("No")])
prior_treatment = st.text_area(t("Prior treatments (medication, therapy)"))
current_medication = st.text_input(t("Current psychotropic medication (name & dose)"))

school_work_problems = st.selectbox(t("Current school/work performance problems?"), ["", t("Yes"), t("No")])
learning_history = st.selectbox(t("History of learning difficulties or special education?"), ["", t("Yes"), t("No")])
family_history = st.text_area(t("Family history of ADHD or psychiatric disorders (if known)"))
medical_history = st.text_area(t("Relevant medical history (e.g., seizures, head injury, chronic illness)"))
sleep_problems = st.selectbox(t("Sleep problems?"), ["", t("Yes"), t("No")])
substance_use = st.selectbox(t("Substance use (adolescent/adult)?"), ["", t("No"), t("Yes"), t("Prefer not to say")])
referral_reason = st.text_area(t("Reason for referral / main concern"))

# -------------------------
# ASRS-6 screener (adult brief)
# -------------------------
st.header(t("ASRS-6 screener (brief adult items)"))
# -------------------------
# Finish ASRS-6 items (complete 6 items)
# -------------------------
asrs_items += [
    "How often do you have problems remembering appointments or obligations?",
    "How often do you have difficulty finishing projects or chores (even those you enjoy)?",
    "How often do you have difficulty concentrating on what people say to you, even when they are speaking to you directly?"
]
# display ASRS
asrs_answers = {}
asrs_options = ["", t("Never"), t("Rarely"), t("Sometimes"), t("Often"), t("Very often")]
for i, item in enumerate(asrs_items, start=1):
    asrs_answers[f"ASRS_{i}"] = st.selectbox(f"ASRS {i}. {t(item)}", asrs_options, key=f"asrs_{i}")

# compute ASRS numeric score (map: Never=0, Rarely=1, Sometimes=2, Often=3, Very often=4)
score_map = {t("Never"):0, t("Rarely"):1, t("Sometimes"):2, t("Often"):3, t("Very often"):4, "": None}
asrs_score = None
try:
    numeric = [score_map[asrs_answers[f"ASRS_{i}"]] for i in range(1, len(asrs_items)+1)]
    if None not in numeric:
        asrs_score = sum(numeric)
        st.write(t("ASRS total score:"), asrs_score)
    else:
        st.info(t("Complete all ASRS items to see the screener score."))
except Exception:
    asrs_score = None

# -------------------------
# Safety / suicidality (urgent)
# -------------------------
st.header(t("Safety"))
suicidality = st.selectbox(t("Any current thoughts of self-harm or suicide?"), ["", t("No"), t("Yes, passive thoughts"), t("Yes, active thoughts/plan")])
if suicidality == t("Yes, active thoughts/plan"):
    st.error(t("URGENT: The person reports active suicidal thoughts or a plan. Please stop the form and contact emergency services or the on-call clinician immediately."))
    st.stop()

# -------------------------
# Consent & submit
# -------------------------
st.header(t("Consent & Submit"))
consent = st.checkbox(t("I consent to storing my (or my child's) data for clinical/assessment purposes."))
agree_save = consent

if st.button(t("Submit")):
    # required checks
    missing_fields = []
    if not name.strip(): missing_fields.append(t("Name"))
    if not email.strip(): missing_fields.append(t("Email"))
    if not phone.strip(): missing_fields.append(t("Phone"))
    # require all DSM items answered
    if any(v == "" for v in sym_answers.values()):
        missing_fields.append(t("All DSM-5 symptom items"))
    if any(v == "" for v in com := { } ):  # placeholder to avoid lint error; real comorbidities handled below
        pass

    if not functional_impairment.strip():
        missing_fields.append(t("Functional impairment description"))
    if not multi_setting or multi_setting == "":
        missing_fields.append(t("Multi-setting question"))
    if not consent:
        missing_fields.append(t("Consent"))

    if missing_fields:
        st.error(t("Please complete the following required fields:") + " " + ", ".join(missing_fields))
    else:
        # Prepare header if sheet is empty
        try:
            header = sheet.row_values(1)
            if not header:
                header = [
                    "Participant_ID","Name","Email","Phone","DOB_or_Age","Gender","Responder","Language",
                    "Age_of_onset","Onset_before_12","Duration","Multi_setting","Functional_impairment",
                    "Prior_diagnosis","Prior_treatment","Current_medication","School_work_problems",
                    "Learning_history","Family_history","Medical_history","Sleep_problems","Substance_use",
                    "Referral_reason","Suicidality","Consent","ASRS_score","Submission_timestamp"
                ]
                header += [f"Symptom_{i}" for i in range(1,19)]
                header += [f"ASRS_{i}" for i in range(1, len(asrs_items)+1)]
                sheet.append_row(header)
        except Exception as e:
            st.error(t("Error preparing Google Sheet header:") + f" {e}")
            st.stop()

        # Build row
        row = [
            participant_id, name, email, phone, dob_or_age, gender, responder, lang_choice,
            age_of_onset, onset_before_12, duration_months, multi_setting, functional_impairment,
            prior_diagnosis, prior_treatment, current_medication, school_work_problems,
            learning_history, family_history, medical_history, sleep_problems, substance_use,
            referral_reason, suicidality, "Yes" if consent else "No", asrs_score if asrs_score is not None else ""
        ]
        # add symptoms
        row += [sym_answers[f"Symptom_{i}"] for i in range(1,19)]
        # add ASRS items
        row += [asrs_answers[f"ASRS_{i}"] for i in range(1, len(asrs_items)+1)]
        # timestamp
        row += [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

        # Append to sheet
        try:
            sheet.append_row(row)
            st.success(t("Submission successful. Thank you — the clinician will review the results."))
        except Exception as e:
            st.error(t("Error submitting data to Google Sheets:") + f" {e}")




