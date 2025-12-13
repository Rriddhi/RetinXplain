# RetinXplain Extension Implementation

## Overview

This document describes the custom RetinXplain extension that adds AI-powered DR (Diabetic Retinopathy) classification, segmentation overlays, and explainability features to the OHIF viewer.

## Architecture

### Extension Structure

The extension is located at: `web/ohif/platform/app/src/extensions/retinxplain/`

```
retinxplain/
├── index.tsx                    # Main extension definition
├── id.js                        # Extension ID
├── getCommandsModule.ts         # Commands for AI backend calls
├── getPanelModule.tsx           # Custom panels (AI Results, LLM Explanation)
├── getCustomizationModule.tsx   # Viewport overlay customizations
└── useAutoPredict.ts            # Hook for auto-prediction on image load
```

### Key Components

#### 1. Commands Module (`getCommandsModule.ts`)

Provides commands to interact with the AI backend:

- **`predictDR`**: Calls `/predict` endpoint with image data, stores results in display set metadata
- **`getLLMExplanation`**: Calls `/explain` endpoint to get text explanation
- **`toggleGradCAMOverlay`**: Toggles Grad-CAM overlay on/off
- **`toggleSegmentationOverlay`**: Toggles lesion segmentation overlay on/off

#### 2. Panel Module (`getPanelModule.tsx`)

Two custom panels:

- **AI Results Panel**: Shows DR grade, confidence, and other conditions
- **LLM Explanation Panel**: Displays AI-generated text explanation

#### 3. Customization Module (`getCustomizationModule.tsx`)

Adds viewport overlay showing DR grade and confidence in the top-right corner.

#### 4. Auto-Prediction Hook (`useAutoPredict.ts`)

Automatically triggers AI prediction when new display sets are loaded (if `autoPredict: true` in config).

## Configuration

The `local.js` config file has been updated with:

```javascript
{
  // AI endpoints
  ai: {
    predictEndpoint: 'http://localhost:8000/predict',
    explainEndpoint: 'http://localhost:8000/explain',
    autoPredict: true,
  },

  // Custom panels
  ui: {
    rightPanels: [
      { id: 'retinxplain-ai-results', name: 'AI Results' },
      { id: 'retinxplain-llm-explanation', name: 'AI Explanation' },
    ],
    toolbarButtons: [
      { id: 'toggle-gradcam', label: 'Grad-CAM', command: 'toggleGradCAMOverlay' },
      { id: 'toggle-segmentation', label: 'Segmentation', command: 'toggleSegmentationOverlay' },
    ],
  },
}
```

## Backend API Contract

### `/predict` Endpoint

**Request:**
- Method: `POST`
- Body: `FormData` with `image` field (DICOM file)

**Response:**
```json
{
  "disease": {
    "primary": "Diabetic Retinopathy",
    "dr_grade": 2,
    "dr_grade_label": "Moderate",
    "confidence": 0.78,
    "other_conditions": [
      { "name": "AMD", "status": "not_evaluated" },
      { "name": "Glaucoma", "status": "not_evaluated" },
      { "name": "Cataract", "status": "not_evaluated" }
    ]
  },
  "explainability": {
    "gradcam_overlay_id": "gradcam-<sopInstanceUid>",
    "segmentation_mask_id": "seg-<sopInstanceUid>",
    "lime_overlay_id": "lime-<sopInstanceUid>"
  }
}
```

### `/explain` Endpoint

**Request:**
- Method: `POST`
- Body: JSON with `displaySetInstanceUID` and `prediction`

**Response:**
```json
{
  "text": "The model predicts Moderate DR (grade 2) with 0.74 confidence...",
  "explanation": "..." // Alternative field name
}
```

## Integration Points

### Extension Loading

The extension is loaded in `App.tsx`:

```typescript
import retinxplainExtension from './extensions/retinxplain';

// Added to defaultExtensions before appInit
const extensionsWithRetinxplain = [...defaultExtensions, retinxplainExtension];
```

### Display Set Metadata

Prediction results are stored in display set metadata:

```javascript
displaySet.retinxplainPrediction = {
  disease: { ... },
  explainability: { ... }
}
```

Panels subscribe to `displaySetMetadataChanged` events to update when predictions arrive.

## Features Implemented

✅ **DR Classification**: Shows grade (0-4) and confidence  
✅ **Other Conditions**: Placeholder support for AMD, Glaucoma, Cataract  
✅ **AI Results Panel**: Displays prediction results  
✅ **LLM Explanation Panel**: Shows AI-generated explanations  
✅ **Viewport Overlay**: DR grade and confidence in viewport  
✅ **Auto-Prediction**: Automatically predicts when images load  
✅ **Toolbar Buttons**: Toggle Grad-CAM and segmentation overlays (UI ready, overlay rendering needs implementation)

## Next Steps / TODO

### Overlay Rendering

The overlay toggle commands are implemented, but the actual rendering of Grad-CAM and segmentation overlays on the viewport needs to be completed. This would involve:

1. Fetching overlay images from backend (using overlay IDs from prediction response)
2. Rendering as image layers on top of the original image in Cornerstone
3. Managing opacity and visibility toggles

### Image Data Handling

The `useAutoPredict` hook needs refinement for different image data sources:
- Local file uploads (dicomlocal)
- DICOMWeb URLs
- Base64 encoded images

### Error Handling

Add more robust error handling for:
- Network failures
- Invalid image formats
- Backend errors

### UI Polish

- Better loading states
- Error messages in panels
- Icon definitions for custom toolbar buttons
- Styling improvements

## Testing

To test the implementation:

1. Start the backend API on `http://localhost:8000`
2. Start the OHIF dev server: `cd web/ohif/platform/app && yarn dev`
3. Load a DR fundus image (DICOM format)
4. Check the right panels for AI results and explanation
5. Use toolbar buttons to toggle overlays (when implemented)

## Notes

- The extension is loaded directly from source, not as a separate package
- All TypeScript/React code is in the extension directory
- Configuration is passed through `appConfig` to extension modules
- The extension follows OHIF v3 extension patterns

