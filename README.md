# AI-For-All Website

A static website for the AI-For-All initiative, focused on empowering young minds with ethical and inclusive AI education.

## Structure

- `index.html` - Main website file
- `styles.css` - Styling
- `script.js` - JavaScript functionality
- `static/images/` - Contains website images and logos

## Viewing the Website

You can view the website in two ways:

1. **Direct Method**: Simply open `index.html` in your web browser
2. **Using Python's HTTP Server**:
   ```bash
   python3 -m http.server 8000
   ```
   Then visit `http://localhost:8000` in your browser

## Development

This is a static website that can be edited using any text editor. The website uses:
- HTML5 for structure
- CSS3 for styling
- Vanilla JavaScript for interactivity
- Font Awesome for icons

## Deployment

The website can be deployed to any static hosting service like:
- GitHub Pages
- Netlify
- Vercel
- Amazon S3

# Editor.js Setup

## Core Editor.js
- Core Editor.js: https://unpkg.com/@editorjs/editorjs@2.30.8/dist/editorjs.umd.js
- Header Plugin: https://unpkg.com/@editorjs/header@2.8.0/dist/header.umd.js
- Paragraph Plugin: https://unpkg.com/@editorjs/paragraph@2.11.2/dist/paragraph.umd.cjs

## Additional Plugins
- Code Plugin: https://unpkg.com/@editorjs/code@2.8.0/dist/code.umd.js
- Marker Plugin: https://unpkg.com/@editorjs/marker@1.4.0/dist/marker.umd.js
- Inline Code Plugin: https://unpkg.com/@editorjs/inline-code@1.4.0/dist/inline-code.umd.js
- List Plugin: https://unpkg.com/@editorjs/list@1.9.0/dist/list.umd.js
- Quote Plugin: https://unpkg.com/@editorjs/quote@2.5.0/dist/quote.umd.js

## Installation
1. Create directory: `static/js/editorjs`
2. Download each file and save with `.min.js` extension
3. Update template to use local files 