import numpy as np

def summarize_lesions(mask_dict: dict) -> str:
    """
    mask_dict: {"ma": np.array(H,W), "he": ..., "ex": ...}
    Returns a simple English summary.
    """
    parts = []
    for lesion_type, mask in mask_dict.items():
        area = float(mask.sum()) / (mask.shape[0] * mask.shape[1])
        if area < 0.001:
            severity = "none or minimal"
        elif area < 0.01:
            severity = "mild"
        elif area < 0.05:
            severity = "moderate"
        else:
            severity = "severe"

        parts.append(f"{lesion_type}: {severity} involvement")

    return "; ".join(parts)
