# RetinXplain Architecture Overview

This document explains how the RetinXplain project is structured and how all the components work together.

## Project Structure

```
retinxplain/
├── src/                    # Python backend (FastAPI)
│   ├── api/               # API endpoints
│   ├── inference/         # AI model loading and prediction
│   ├── data/              # Image preprocessing
│   └── utils/             # Utilities
└── web/ohif/              # OHIF Viewer frontend
    └── platform/app/      # Main OHIF application
```

## How OHIF Viewer Works

### 1. **Configuration System** (`local.js`)

The configuration file (`web/ohif/platform/app/public/config/local.js`) is the **entry point** that controls everything:

- **Location**: `web/ohif/platform/app/public/config/local.js`
- **How it's loaded**: 
  - At build time, webpack copies this file to `dist/app-config.js`
  - At runtime, `index.js` reads `window.config` from this file
  - The `APP_CONFIG` environment variable determines which config file to use

**Flow:**
```
Build Process:
  APP_CONFIG=config/local.js 
  → webpack copies local.js → dist/app-config.js
  → HTML loads app-config.js → window.config is set

Runtime:
  index.js → reads window.config → passes to App.tsx → appInit.js
```

### 2. **Application Initialization** (`appInit.js`)

Located at: `web/ohif/platform/app/src/appInit.js`

**What it does:**
1. Creates core managers (Commands, Services, Extensions, Hotkeys)
2. Registers services (Measurement, DisplaySet, Toolbar, etc.)
3. Loads extensions from `pluginConfig.json` + config extensions
4. Loads modes from `pluginConfig.json` + config modes
5. Registers data sources

**Key Code:**
```javascript
// Loads extensions (image rendering, UI components)
const loadedExtensions = await loadModules([...defaultExtensions, ...appConfig.extensions]);

// Registers data sources (where images come from)
await extensionManager.registerExtensions(loadedExtensions, appConfig.dataSources);

// Loads modes (how images are displayed)
const loadedModes = await loadModules([...appConfig.modes, ...defaultModes]);
```

### 3. **Extensions System**

**Location**: `web/ohif/platform/app/pluginConfig.json`

Extensions are **pre-built modules** that add functionality:

- **@ohif/extension-default**: Core UI (study list, panels, navigation)
- **@ohif/extension-cornerstone**: Image rendering engine (displays DICOM images)
- **@ohif/extension-measurement-tracking**: Measurement tools
- Others: PDF viewer, video viewer, segmentation, etc.

**How they're linked:**
1. `pluginConfig.json` lists available extensions
2. Build process (`writePluginImportsFile.js`) generates `pluginImports.js`
3. `pluginImports.js` imports all extensions and adds them to `window`
4. `appInit.js` loads them dynamically

### 4. **Modes System**

**Location**: `web/ohif/platform/app/pluginConfig.json`

Modes define **how images are displayed** and what tools are available:

- **@ohif/mode-basic**: Simple image viewer (perfect for DR images)
- **@ohif/mode-longitudinal**: Compare studies over time
- **@ohif/mode-segmentation**: Segmentation tools
- **@ohif/mode-microscopy**: Microscopy images

**How they work:**
- Each mode has a `modeFactory` function
- The mode defines viewport layouts, toolbar buttons, hanging protocols
- Your config specifies which modes to enable

### 5. **Data Sources**

Data sources define **where images come from**:

**Types:**
- **dicomlocal**: Local file loading (drag & drop DICOM files)
- **dicomjson**: Load from JSON format
- **dicomweb**: Load from DICOMWeb server (QIDO-RS, WADO-RS)

**How they work:**
```javascript
{
  namespace: '@ohif/extension-default.dataSourcesModule.dicomlocal',
  sourceName: 'dicomlocal',
  configuration: { friendlyName: 'Local DICOM Files' }
}
```

The extension provides the data source module, which handles:
- File loading
- DICOM parsing
- Study/series organization
- Image retrieval

### 6. **Build Process**

**Webpack Configuration**: `web/ohif/platform/app/.webpack/webpack.pwa.js`

**Steps:**
1. Reads `APP_CONFIG` environment variable
2. Copies selected config file to `dist/app-config.js`
3. Bundles all extensions and modes
4. Generates `pluginImports.js` from `pluginConfig.json`
5. Creates production bundle

**Key files:**
- `webpack.pwa.js`: Main webpack config
- `writePluginImportsFile.js`: Generates plugin imports
- `pluginConfig.json`: Lists available extensions/modes

### 7. **Runtime Flow**

```
1. Browser loads index.html
   ↓
2. HTML loads app-config.js (your local.js)
   ↓
3. index.js reads window.config
   ↓
4. index.js calls App.tsx with config
   ↓
5. App.tsx calls appInit.js
   ↓
6. appInit.js:
   - Creates managers
   - Loads extensions
   - Loads modes
   - Registers data sources
   ↓
7. App.tsx renders React components
   ↓
8. User interacts → loads images → displays in viewport
```

## File Loading Flow (for DR Images)

When a user loads a DR image:

```
1. User drags DICOM file or clicks "Load"
   ↓
2. dicomlocal data source receives file
   ↓
3. FileLoaderService parses DICOM file
   ↓
4. Creates study/series/instance structure
   ↓
5. DisplaySetService organizes images
   ↓
6. Cornerstone extension renders image
   ↓
7. Image appears in viewport
```

## Key Directories Explained

### `web/ohif/platform/app/`
- **Main application code**
- `src/`: React components, routes, services
- `public/config/`: Configuration files
- `.webpack/`: Build configuration

### `web/ohif/platform/core/`
- **Core OHIF framework**
- Services, managers, utilities
- Shared across all OHIF apps

### `web/ohif/extensions/`
- **Extension packages**
- Each extension is a separate package
- Can be enabled/disabled via config

### `web/ohif/modes/`
- **Mode packages**
- Each mode defines a viewing experience
- Can be enabled/disabled via config

## How to Customize

### Add a new data source:
1. Add to `dataSources` array in `local.js`
2. Configure the endpoint/behavior

### Add a new extension:
1. Install package: `yarn add @ohif/extension-name`
2. Add to `pluginConfig.json`
3. Add to `extensions` array in `local.js`

### Change UI:
1. Modify `ui` section in `local.js`
2. Customize panels, toolbar buttons
3. Or create custom React components

### Connect to your backend:
1. Add DICOMWeb data source pointing to your API
2. Or use `dicomjson` to load from your API's JSON response
3. Configure endpoints in data source configuration

## Environment Variables

- **APP_CONFIG**: Which config file to use (default: `config/default.js`)
- **NODE_ENV**: `development` or `production`
- **OHIF_PORT**: Dev server port (default: 3000)
- **PUBLIC_URL**: Base URL path (default: `/`)

## Summary

**The config file (`local.js`) is the control center:**
- It specifies which extensions to load (image rendering, UI)
- It specifies which modes to use (viewing experience)
- It specifies data sources (where images come from)
- It customizes UI and branding

**Everything else is pre-built:**
- Extensions are in `node_modules/@ohif/extension-*`
- Modes are in `node_modules/@ohif/mode-*`
- The build system links them together
- Runtime loads them dynamically

**For DR images specifically:**
- Use `dicomlocal` data source for file uploads
- Use `@ohif/extension-cornerstone` for rendering
- Use `@ohif/mode-basic` for simple viewing
- Enable `showStudyList: true` to allow image selection

