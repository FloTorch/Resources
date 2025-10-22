import os
import streamlit as st
from graphs.medical_coder_graph import build_medical_coder_graph
from utils.samples import patient_report_1


st.set_page_config(
    page_title="Medical Coder",
    page_icon="🩺",
)

st.title("🩺 Medical Coder")
st.write("Please submit patient report.")

with st.form("patient_report_form"):
    user_text = st.text_area("Patient report", value=patient_report_1, height=500)
    submitted = st.form_submit_button("Submit")
    medical_coder_graph = build_medical_coder_graph()

    if submitted:
        result = medical_coder_graph(user_text)
        medical_coder_graph = build_medical_coder_graph() # rebuild graph to refresh state

patient_summary_path = "output/patient_summary.json"
if os.path.exists(patient_summary_path):
    with open(patient_summary_path, "rb") as file:
        st.download_button(
            label="Patient summary",
            data=file,
            file_name="diagnosis_data.json",
            mime="application/json",
        )
else:
    st.error(f"File not found at: {patient_summary_path}")

diagnosis_data_path = "output/diagnosis_data.json"
if os.path.exists(patient_summary_path):
    with open(patient_summary_path, "rb") as file:
        st.download_button(
            label="Patient summary",
            data=file,
            file_name="diagnosis_data.json",
            mime="application/json",
        )
else:
    st.error(f"File not found at: {diagnosis_data_path}")

procedure_data_path = "output/procedure_data.json"
if os.path.exists(patient_summary_path):
    with open(patient_summary_path, "rb") as file:
        st.download_button(
            label="Patient summary",
            data=file,
            file_name="procedure_data.json",
            mime="application/json",
        )
else:
    st.error(f"File not found at: {procedure_data_path}")