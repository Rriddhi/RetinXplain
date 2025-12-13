#!/usr/bin/env python3
"""Simple notebook to HTML export with all images embedded."""

from nbconvert.filters import widgetsdatatypefilter
widgetsdatatypefilter.WidgetsDataTypeFilter.__call__ = lambda self, o: list(o.get('data', {}).keys()) if isinstance(o, dict) and 'data' in o else []

from nbconvert import HTMLExporter
import nbformat
import re

nb = nbformat.read('efficientnet_b4_RetinXplain.ipynb', 4)

# Collect all images
all_images = []
for cell in nb.cells:
    if cell.cell_type == 'code' and hasattr(cell, 'outputs') and cell.outputs:
        for output in cell.outputs:
            if 'data' in output and 'image/png' in output['data']:
                all_images.append(output['data']['image/png'])

# Export
exporter = HTMLExporter()
exporter.embed_images = True
html, _ = exporter.from_notebook_node(nb)

# Build mapping: code cell index -> images
cell_images = {}
code_idx = 0
for cell in nb.cells:
    if cell.cell_type == 'code':
        imgs = []
        if hasattr(cell, 'outputs') and cell.outputs:
            for output in cell.outputs:
                if 'data' in output and 'image/png' in output['data']:
                    imgs.append(output['data']['image/png'])
        if imgs:
            cell_images[code_idx] = imgs
        code_idx += 1

# Map code cells with images to output_wrappers (JupyterLab template)
code_cells = list(re.finditer(r'<div class="jp-Cell jp-CodeCell jp-Notebook-cell"', html))
output_wrappers = list(re.finditer(r'<div class="jp-Cell-outputWrapper"', html))

# Map: code cell index -> wrapper index (only cells with outputs have wrappers)
code_to_wrapper = {}
wrapper_idx = 0
for code_idx, cell in enumerate(nb.cells):
    if cell.cell_type == 'code' and hasattr(cell, 'outputs') and cell.outputs:
        if wrapper_idx < len(output_wrappers):
            code_to_wrapper[code_idx] = wrapper_idx
            wrapper_idx += 1

# Collect all images in order
all_images = []
for code_idx in sorted(cell_images.keys()):
    all_images.extend(cell_images[code_idx])

# Collect injection points first
injection_points = []
for wrapper_idx, wrapper in enumerate(output_wrappers):
    wrapper_start = wrapper.start()
    wrapper_snippet = html[wrapper_start:min(wrapper_start+50000, len(html))]
    
    # If this wrapper doesn't have image data URLs
    if 'data:image/png;base64' not in wrapper_snippet and 'data:image/jpeg;base64' not in wrapper_snippet:
        output_match = re.search(r'<div class="jp-OutputArea jp-Cell-outputArea"', wrapper_snippet)
        if output_match:
            output_start = wrapper_start + output_match.start()
            depth = 0
            pos = output_start + output_match.end()
            output_end = pos
            search_limit = min(output_start + 20000, len(html))
            while pos < search_limit:
                if html[pos:pos+4] == '<div':
                    depth += 1
                    pos = html.find('>', pos) + 1
                elif html[pos:pos+6] == '</div>':
                    if depth == 0:
                        output_end = pos + 6
                        break
                    depth -= 1
                    pos += 6
                else:
                    pos += 1
            
            if output_end > output_start:
                injection_points.append((output_end, wrapper_idx))

# Inject images in reverse order
for i, (output_end, wrapper_idx) in enumerate(reversed(injection_points)):
    if i < len(all_images):
        img_data = all_images[-(i+1)]
        img_html = f'<div class="jp-OutputArea-child"><div class="jp-OutputPrompt jp-OutputArea-prompt"></div><div class="jp-RenderedImage jp-OutputArea-output" tabindex="0"><img alt="No description has been provided for this image" class="" src="data:image/png;base64,{img_data}"/></div></div>'
        html = html[:output_end-6] + '\n' + img_html + '\n</div>' + html[output_end:]

with open('efficientnet_b4_RetinXplain.html', 'w', encoding='utf-8') as f:
    f.write(html)

img_count = html.count('data:image/png;base64') + html.count('data:image/jpeg;base64')
print(f"✅ Exported with {img_count} embedded images")

