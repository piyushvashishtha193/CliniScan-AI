import streamlit as st

st.title("🏥 CliniScan AI")

patient_name = st.text_input(
    "Enter Patient Name"
)

if st.button("Analyze Report"):

    if patient_name:
        st.success(
            f"Analysis started for {patient_name}"
        )
    else:
        st.error(
            "Please enter a patient name."
        )