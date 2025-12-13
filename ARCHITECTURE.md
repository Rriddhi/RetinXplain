# RetinXplain Architecture

This document describes the architecture and design of the RetinXplain system.

## System Overview

RetinXplain is a full-stack web application for diabetic retinopathy classification with explainability features. It consists of:

1. **Backend**: FastAPI-based REST API serving PyTorch models
2. **Frontend**: React-based web interface for image upload and result visualization
3. **Model**: ResNet50-based classifier with explainability modules

## Architecture Diagram

```
┌─────────────────┐
│   React Frontend │
│   (Port 5000)    │
│                  │
│  - Image Upload  │
│  - Results View  │
│  - Overlays      │
└────────┬─────────┘
         │ HTTP/REST
         │
┌────────▼─────────┐
│  FastAPI Backend  │
│   (Port 8000)     │
│                   │
│  - /api/dr/predict│
│  - /health        │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Model  │ │Explain │
│Loader │ │Modules │
└───┬───┘ └───┬────┘
    │         │
┌───▼─────────▼───┐
│  PyTorch Model  │
│   (ResNet50)    │
└─────────────────┘
```

## Backend Architecture

### Directory Structure

```
src/
├── api/
│   └── main.py              # FastAPI app, route handlers
├── inference/
│   ├── model_loader.py      # Model loading and initialization
│   ├── predictor.py         # Main prediction pipeline
│   ├── explainability.py    # Grad-CAM++, LIME, SHAP implementations
│   └── llm_explainer.py     # LLM-based text explanations (optional)
├── data/
│   ├── image_preprocess.py  # Image preprocessing utilities
│   └── transforms.py        # PyTorch transforms
├── utils/
│   ├── image_io.py          # Image I/O operations
│   └── logging_utils.py     # Logging configuration
└── config.py                # Configuration constants
```

### Core Components

#### 1. API Layer (`src/api/main.py`)

**Responsibilities:**
- Handle HTTP requests
- File upload processing
- Response formatting
- CORS configuration

**Key Endpoints:**
- `POST /api/dr/predict`: Main prediction endpoint
- `GET /health`: Health check

**Flow:**
```
1. Receive image upload
2. Save to uploads/ directory
3. Call predictor module
4. Format and return results
```

#### 2. Inference Pipeline (`src/inference/predictor.py`)

**Responsibilities:**
- Orchestrate prediction workflow
- Coordinate model inference and explainability
- Save generated overlays

**Workflow:**
```
1. Load and preprocess image
2. Run model inference
3. Generate explainability overlays (Grad-CAM++, LIME, SHAP)
4. Return results with file paths
```

#### 3. Model Loader (`src/inference/model_loader.py`)

**Responsibilities:**
- Load trained PyTorch model
- Initialize model architecture
- Handle device selection (CPU/CUDA/MPS)
- Cache model in memory

**Features:**
- Lazy loading (loads on first use)
- Device auto-detection
- Model state validation

#### 4. Explainability Module (`src/inference/explainability.py`)

**Responsibilities:**
- Generate Grad-CAM++ overlays
- Generate LIME explanations
- Generate SHAP visualizations
- Save overlay images

**Methods:**
- `generate_gradcam`: Gradient-weighted activation maps
- `generate_lime`: Local interpretable explanations
- `generate_shap`: SHapley additive explanations

#### 5. Data Preprocessing (`src/data/`)

**Components:**
- `image_preprocess.py`: Image loading, resizing, normalization
- `transforms.py`: PyTorch transform pipelines

**Preprocessing Steps:**
1. Resize to 256x256
2. Center crop to 224x224
3. Convert to tensor
4. Normalize with ImageNet statistics

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main application component
│   ├── components/
│   │   ├── ImageUpload.jsx  # Image upload with drag-and-drop
│   │   ├── ReportPanel.jsx  # Prediction results display
│   │   └── FeedbackPanel.jsx # User feedback form
│   ├── main.jsx            # React entry point
│   └── index.css           # Global styles
├── package.json
└── vite.config.js          # Vite build configuration
```

### Component Hierarchy

```
App
├── Header
├── ImageUpload
│   └── Dropzone
├── ReportPanel
│   ├── Prediction Summary
│   ├── Probability Chart
│   └── Overlay Images
└── FeedbackPanel
    └── Feedback Form
```

### Key Components

#### 1. App.jsx
- Main application state management
- Coordinates between upload, prediction, and feedback
- Error handling

#### 2. ImageUpload.jsx
- Drag-and-drop file upload
- Image preview
- API integration for prediction

#### 3. ReportPanel.jsx
- Displays prediction results
- Shows DR grade and confidence
- Renders explainability overlays
- Probability distribution visualization

#### 4. FeedbackPanel.jsx
- Collects user feedback
- Submits feedback to backend
- Resets state after submission

## Data Flow

### Prediction Flow

```
1. User uploads image (Frontend)
   ↓
2. POST /api/dr/predict with image file (Backend)
   ↓
3. Save image to uploads/ directory
   ↓
4. Load and preprocess image
   ↓
5. Run model inference
   ↓
6. Generate explainability overlays
   ↓
7. Save overlays to uploads/
   ↓
8. Return JSON response with paths
   ↓
9. Frontend displays results and overlays
```

### File Storage

```
uploads/
└── YYYY-MM-DD/
    ├── {uuid}_original.png
    ├── {uuid}_gradcam.png
    ├── {uuid}_lime.png
    └── {uuid}_shap.png
```

## Model Architecture

### ResNet50 Configuration

- **Base Model**: torchvision.models.resnet50
- **Input**: 3-channel RGB images, 224x224
- **Output**: 5-class logits (DR grades 0-4)
- **Modifications**: Final fully-connected layer changed to 5 outputs

### Class Mapping

```
0: "No DR"
1: "Mild"
2: "Moderate"
3: "Severe"
4: "Proliferative DR"
```

## Explainability Methods

### 1. Grad-CAM++

**Implementation**: `grad-cam` library
**Output**: Heatmap overlay showing important regions
**Use Case**: Visual attention visualization

### 2. LIME

**Implementation**: `lime` library with image explainer
**Output**: Superpixel-based importance map
**Use Case**: Local interpretability

### 3. SHAP

**Implementation**: Custom implementation
**Output**: Feature importance visualization
**Use Case**: Global model interpretability

## Configuration Management

### Backend Config (`src/config.py`)

- Model paths
- Image preprocessing parameters
- Device selection
- Class definitions

### Environment Variables

- API keys (LLM services)
- Service endpoints
- Feature flags

## Error Handling

### Backend

- File upload validation
- Model loading errors
- Image processing errors
- Graceful degradation

### Frontend

- Network error handling
- Invalid file type handling
- Loading states
- User-friendly error messages

## Security Considerations

### Current State

- CORS enabled for all origins (should be restricted in production)
- File upload validation needed
- No authentication/authorization

### Production Recommendations

- Restrict CORS to frontend domain
- Add file type and size validation
- Implement authentication
- Add rate limiting
- Sanitize file paths
- Use HTTPS

## Performance Optimizations

### Backend

- Model caching (loaded once, reused)
- Async file I/O
- Efficient image preprocessing
- Device selection (GPU/MPS acceleration)

### Frontend

- Image compression before upload
- Lazy loading of overlay images
- Optimized React rendering
- Vite for fast builds

## Deployment

### Backend

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run build
# Serve dist/ directory with static file server
```

### Production Considerations

- Use production ASGI server (Gunicorn + Uvicorn workers)
- Set up reverse proxy (Nginx)
- Configure static file serving
- Enable HTTPS
- Set up monitoring and logging

## Future Enhancements

- [ ] Batch prediction support
- [ ] Model versioning
- [ ] User authentication
- [ ] Database for predictions and feedback
- [ ] Real-time prediction streaming
- [ ] Additional explainability methods
- [ ] Model ensemble support
- [ ] API rate limiting
- [ ] Comprehensive test suite
