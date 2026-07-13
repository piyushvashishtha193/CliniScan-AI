from app.services.gemini import generate_clinical_summary


transcript = """
Doctor: Good morning. What brings you here today?

Patient: I have had headaches for the past three weeks.

Doctor: Do you have a fever?

Patient: No fever.

Doctor: I recommend staying hydrated and taking the prescribed medication.
"""


summary = generate_clinical_summary(transcript)

print("\nGenerated Clinical Summary:\n")
print(summary)