CLINICAL_EXPLANATION_PROMPT = """
You are an assistant helping explain diabetic retinopathy predictions.

Model prediction: {dr_grade}
Model confidence: {confidence:.2f}
Lesion summary: {lesion_summary}

Explain in 1–2 short paragraphs:
- why this grade is plausible based on the lesions
- what a clinician should pay attention to
Avoid making treatment recommendations.
"""