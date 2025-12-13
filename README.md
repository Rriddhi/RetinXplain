# RetinXplain

AI-Powered Diabetic Retinopathy (DR) Screening System with Explainability

RetinXplain is a comprehensive deep learning system for automated diabetic retinopathy classification from fundus images. It provides accurate DR grading (0-4) along with multiple explainability visualizations (Grad-CAM++, LIME, SHAP) to help clinicians understand model predictions.

## Features

- **DR Classification**: 5-class classification (No DR, Mild, Moderate, Severe, Proliferative DR)
- **Explainability**: Multiple visualization methods (Grad-CAM++, LIME, SHAP overlays)
- **Modern Web Interface**: React-based frontend with drag-and-drop image upload
- **RESTful API**: FastAPI backend with automatic documentation
- **LLM Explanations**: AI-generated text explanations of predictions (optional)
- **Feedback System**: Collect and log user feedback for model improvement

## Project Structure

```
retinxplain/
├── src/                    # Python backend
│   ├── api/               # FastAPI endpoints
│   ├── inference/         # Model loading, prediction, explainability
│   ├── data/              # Image preprocessing and transforms
│   └── utils/             # Utilities (image I/O, logging)
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── App.jsx        # Main app component
│   └── package.json
├── Notebooks/             # Jupyter notebooks for model training/experimentation
├── models/                # Trained model weights (not in git)
└── uploads/               # Uploaded images and generated overlays (not in git)
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm/yarn
- PyTorch (CPU or GPU/MPS)

### Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if using LLM explainer
   ```

3. **Place model weights:**
   - Download or train the ResNet50 model
   - Place `resnet50_best_cleaned.pt` in `models/` directory

4. **Start backend server:**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5000`

### Usage

1. Open the web interface at `http://localhost:5000`
2. Upload a fundus image (drag & drop or click to select)
3. View the prediction results:
   - DR grade and confidence
   - Probability distribution across all classes
   - Explainability overlays (Grad-CAM++, LIME, SHAP)
   - AI-generated text explanation (if configured)
4. Provide feedback on the prediction quality

## API Endpoints

### `POST /api/dr/predict`

Predict DR classification from a fundus image.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
  "pred_class_idx": 2,
  "pred_class_name": "Moderate",
  "confidence": 0.87,
  "probs": [0.05, 0.08, 0.87, 0.00, 0.00],
  "artifacts": {
    "original_image_path": "2024-01-15/abc123_original.png",
    "gradcam_overlay_path": "2024-01-15/abc123_gradcam.png",
    "lime_overlay_path": "2024-01-15/abc123_lime.png",
    "shap_overlay_path": "2024-01-15/abc123_shap.png"
  }
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Model Details

- **Architecture**: ResNet50
- **Input Size**: 224x224 (resized from 256x256 with center crop)
- **Classes**: 5 DR severity levels (0-4)
- **Normalization**: ImageNet statistics
- **Device Support**: CPU, CUDA (GPU), MPS (Apple Silicon)

## Explainability Methods

1. **Grad-CAM++**: Gradient-weighted Class Activation Mapping showing important regions
2. **LIME**: Local Interpretable Model-agnostic Explanations with superpixel analysis
3. **SHAP**: SHapley Additive exPlanations for feature importance

## Development

### Backend Development

```bash
# Run with auto-reload
uvicorn src.api.main:app --reload

# Run tests (if available)
pytest
```

### Frontend Development

```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

## Configuration

Key configuration in `src/config.py`:
- Model path
- Image preprocessing parameters
- Device selection (auto-detects MPS/CUDA/CPU)
- Class names and mappings

## Environment Variables

See `.env.example` for required environment variables:
- LLM API keys (if using LLM explainer)
- Other service configurations

## License

[Add your license here]

## Citation

If you use this project in your research, please cite:

```bibtex
[Add citation information]
```

## Contributing

[Add contribution guidelines]

## Acknowledgments

[Add acknowledgments]
