import os
from typing import Dict, Optional

from src.config import CLASS_NAMES, LLM_PROVIDER, LLM_MODEL_NAME

def generate_explanation(
    pred_class_idx: int,
    pred_class_name: str,
    confidence: float,
    probs: list,
    clinical_notes: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate patient-friendly and clinician summaries using LLM or template.
    
    Args:
        pred_class_idx: Predicted class index (0-4)
        pred_class_name: Predicted class name
        confidence: Confidence score
        probs: List of probabilities for all classes
        clinical_notes: Optional free-text from clinician
    
    Returns:
        Dictionary with 'patient_summary' and 'clinician_summary'
    """
    # Try to use LLM if API key is available
    try:
        if LLM_PROVIDER == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                return _generate_with_openai(
                    pred_class_idx, pred_class_name, confidence, probs, clinical_notes
                )
    except Exception as e:
        print(f"LLM generation failed: {e}, falling back to template")
    
    # Fallback to template-based explanation
    return _generate_template_explanation(pred_class_idx, pred_class_name, confidence, probs)


def _generate_with_openai(
    pred_class_idx: int,
    pred_class_name: str,
    confidence: float,
    probs: list,
    clinical_notes: Optional[str]
) -> Dict[str, str]:
    """Generate explanations using OpenAI API."""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Build prompt for clinician summary
        clinician_prompt = f"""You are a medical AI assistant. Provide a concise clinical summary for a diabetic retinopathy screening result.

Prediction: {pred_class_name} (Grade {pred_class_idx}/4)
Confidence: {confidence:.1%}
Probabilities: {dict(zip([CLASS_NAMES[i] for i in range(5)], [f"{p:.1%}" for p in probs]))}

Provide a brief (2-3 sentences) clinical summary suitable for healthcare professionals, focusing on:
- The severity assessment
- Clinical significance
- Typical findings for this grade
"""
        
        # Build prompt for patient summary
        patient_prompt = f"""You are a medical AI assistant. Provide a patient-friendly explanation for a diabetic retinopathy screening result.

Prediction: {pred_class_name} (Grade {pred_class_idx}/4)
Confidence: {confidence:.1%}

Provide a clear, empathetic explanation (3-4 sentences) suitable for patients, using simple language. Explain:
- What the result means in plain terms
- What they should do next
- Reassurance if appropriate
"""
        
        clinician_response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": clinician_prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        patient_response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": patient_prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        return {
            "clinician_summary": clinician_response.choices[0].message.content.strip(),
            "patient_summary": patient_response.choices[0].message.content.strip()
        }
    except ImportError:
        raise ImportError("openai package not installed. Install with: pip install openai")
    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")


def _generate_template_explanation(
    pred_class_idx: int,
    pred_class_name: str,
    confidence: float,
    probs: list
) -> Dict[str, str]:
    """Generate template-based explanations when LLM is not available."""
    
    grade_descriptions = {
        0: {
            "clinical": "No signs of diabetic retinopathy detected. The retinal image shows no microaneurysms, hemorrhages, or other DR-related lesions. Continue annual screening as recommended for diabetic patients.",
            "patient": "Good news! Your retinal screening shows no signs of diabetic retinopathy. This means your eyes are healthy from a diabetes perspective. Continue with your regular annual eye exams and maintain good blood sugar control."
        },
        1: {
            "clinical": "Mild non-proliferative diabetic retinopathy (NPDR) detected. Presence of microaneurysms only. Low risk of progression. Recommend follow-up screening in 6-12 months.",
            "patient": "Your screening detected mild diabetic retinopathy. This is the earliest stage, with only small changes visible. It's important to monitor this, so your doctor will likely recommend another screening in 6-12 months. Good blood sugar control can help prevent progression."
        },
        2: {
            "clinical": "Moderate NPDR detected. Multiple microaneurysms and/or hemorrhages present, but no severe features. Moderate risk of progression. Recommend ophthalmology referral and follow-up in 3-6 months.",
            "patient": "Your screening shows moderate diabetic retinopathy. There are some changes in your retina that need attention. Your doctor will likely refer you to an eye specialist (ophthalmologist) for a comprehensive exam. Follow-up is typically recommended in 3-6 months."
        },
        3: {
            "clinical": "Severe NPDR detected. Multiple hemorrhages, venous beading, or intraretinal microvascular abnormalities present. High risk of progression to proliferative DR. Urgent ophthalmology referral recommended within 1-2 weeks.",
            "patient": "Your screening detected severe diabetic retinopathy. This requires prompt attention from an eye specialist. Please schedule an appointment with an ophthalmologist within 1-2 weeks. Early treatment can help preserve your vision."
        },
        4: {
            "clinical": "Proliferative diabetic retinopathy (PDR) detected. Presence of neovascularization, vitreous hemorrhage, or retinal detachment. High risk of vision loss. Urgent ophthalmology referral and potential treatment (laser, anti-VEGF) required immediately.",
            "patient": "Your screening shows proliferative diabetic retinopathy, the most advanced stage. This requires immediate medical attention. Please contact an ophthalmologist right away - this is urgent. Treatment options are available that can help preserve your vision."
        }
    }
    
    desc = grade_descriptions.get(pred_class_idx, grade_descriptions[0])
    
    clinician_summary = f"{desc['clinical']} (Confidence: {confidence:.1%})"
    patient_summary = f"{desc['patient']} The AI system is {confidence:.0%} confident in this assessment."
    
    return {
        "clinician_summary": clinician_summary,
        "patient_summary": patient_summary
    }
