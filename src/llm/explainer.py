from .prompts import CLINICAL_EXPLANATION_PROMPT

def get_explanation(dr_grade: str, confidence: float, lesion_summary: str) -> str:
    prompt = CLINICAL_EXPLANATION_PROMPT.format(
        dr_grade=dr_grade,
        confidence=confidence,
        lesion_summary=lesion_summary,
    )

    # TODO: Call your LLM API here.
    # Placeholder: just echo the prompt or a stub string for now.
    explanation = (
        f"(LLM explanation placeholder)\n\n"
        f"Prediction: {dr_grade} (confidence {confidence:.2f}). "
        f"Lesion summary: {lesion_summary}."
    )
    return explanation
