import gradio as gr
from PIL import Image

from src.api.inference_pipeline import run_full_pipeline

def predict(image):
    result = run_full_pipeline(image)
    return (
        result["dr_grade"],
        f"{result['confidence']:.2f}",
        result["gradcam_overlay"],
        result["explanation"],
    )

def create_app():
    with gr.Blocks() as demo:
        gr.Markdown("# RetinXplain – DR Classifier with Explainability")
        with gr.Row():
            with gr.Column():
                img_input = gr.Image(type="pil", label="Upload fundus image")
                btn = gr.Button("Analyze")
            with gr.Column():
                grade_out = gr.Textbox(label="Predicted DR Grade")
                conf_out = gr.Textbox(label="Confidence")
                heatmap_out = gr.Image(label="Grad-CAM Overlay")
                explanation_out = gr.Textbox(label="LLM Explanation", lines=6)

        btn.click(
            fn=predict,
            inputs=[img_input],
            outputs=[grade_out, conf_out, heatmap_out, explanation_out],
        )
    return demo

if __name__ == "__main__":
    app = create_app()
    app.launch()
