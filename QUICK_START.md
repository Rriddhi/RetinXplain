# RetinXplain Viewer - Quick Start

## Server Status

The development server has been restarted and should now be running at:
**http://localhost:3000**

## What's New

The RetinXplain extension has been loaded with the following features:

### ✅ Custom Panels (Right Sidebar)
- **AI Results Panel**: Shows DR grade, confidence, and other conditions
- **LLM Explanation Panel**: Displays AI-generated explanations

### ✅ Viewport Overlay
- DR grade and confidence displayed in top-right corner of viewport

### ✅ Auto-Prediction
- Automatically calls your backend `/predict` endpoint when images are loaded

### ✅ Toolbar Buttons
- Grad-CAM toggle (UI ready, overlay rendering pending)
- Segmentation toggle (UI ready, overlay rendering pending)

## Testing the Viewer

1. **Open the viewer**: Navigate to http://localhost:3000 in your browser

2. **Load a DR image**:
   - Drag and drop a DICOM file into the browser
   - Or use the "Load" button to select a file

3. **Check the panels**:
   - Open the right sidebar
   - Click on "AI Results" panel to see prediction results
   - Click on "AI Explanation" panel to see LLM-generated explanation

4. **View the overlay**:
   - The DR grade and confidence should appear in the top-right of the viewport

## Backend Requirements

Make sure your FastAPI backend is running on `http://localhost:8000` with:

- **POST /predict**: Accepts image file, returns prediction JSON
- **POST /explain**: Accepts prediction data, returns text explanation

## Troubleshooting

### If panels don't appear:
1. Check browser console for errors (F12)
2. Verify the extension loaded: Look for "retinxplain-extension" in console
3. Hard refresh the page (Cmd+Shift+R or Ctrl+Shift+R)

### If predictions don't work:
1. Check that backend is running: `curl http://localhost:8000/health`
2. Check browser Network tab for failed requests
3. Verify CORS is enabled on your backend

### If webpack errors:
1. Check terminal for compilation errors
2. Try stopping and restarting: 
   ```bash
   cd web/ohif/platform/app
   NODE_ENV=development APP_CONFIG=config/local.js yarn run dev
   ```

## Next Steps

1. **Implement overlay rendering**: The toggle commands are ready, but you need to implement the actual Grad-CAM and segmentation overlay rendering on the viewport

2. **Test with real images**: Load actual DR fundus images to test the full workflow

3. **Customize styling**: Adjust panel styles and colors to match your branding

4. **Add error handling**: Improve error messages and loading states

