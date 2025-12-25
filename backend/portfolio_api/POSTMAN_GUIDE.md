# Portfolio Builder API - Postman Testing Guide

## Prerequisites

1. **Start the backend server:**
```bash
cd c:\Users\Zainab\Desktop\CareerPilot-BE
.venv\Scripts\Activate
cd backend
python main.py
```

Server runs at: `http://localhost:8000`

2. **Verify server is running:**
   - In Postman: `GET http://localhost:8000/ping` → Should return `{"message": "pong"}`

---

## Step 1: Generate Portfolio (File Upload)

### Request
- **Method:** `POST`
- **URL:** `http://localhost:8000/portfolio-builder/generate`
- **Body:** `form-data`

| Key | Type | Value |
|-----|------|-------|
| `resume_file` | File | Select your resume PDF/DOCX/TXT |
| `user_prompt` | Text | `Create a modern portfolio with yellow background and black text` |

### Postman Setup
1. Select **POST** method
2. Enter URL: `http://localhost:8000/portfolio-builder/generate`
3. Go to **Body** tab → Select **form-data**
4. Add key `resume_file` → Change type to **File** → Select your resume
5. Add key `user_prompt` → Enter your preferences
6. Click **Send**

### Expected Response
```json
{
  "success": true,
  "project_id": "a1b2c3d4",
  "message": "Portfolio generation started. Use /status/{project_id} to track progress.",
  "output_path": null,
  "zip_download_url": null,
  "preview_url": null,
  "errors": [],
  "warnings": []
}
```

**⚠️ IMPORTANT: Copy the `project_id` (e.g., `a1b2c3d4`)** - you need it for the next steps!

---

## Step 2: Check Generation Status

### Request
- **Method:** `GET`
- **URL:** `http://localhost:8000/portfolio-builder/status/a1b2c3d4`

**Replace `a1b2c3d4` with YOUR project_id from Step 1!**

### Progress Updates
| Progress | Status | Meaning |
|----------|--------|---------|
| 0% | pending | Queued for processing |
| 10-20% | processing | Starting, parsing resume |
| 30% | processing | Running workflow |
| 90% | processing | Processing results |
| 100% | completed | Done! Check `result` field |

### Example Responses

**While processing (keep polling every 5-10 seconds):**
```json
{
  "project_id": "a1b2c3d4",
  "status": "processing",
  "progress": 30,
  "current_step": "Running portfolio generation workflow...",
  "result": null
}
```

**When completed (progress = 100):**
```json
{
  "project_id": "a1b2c3d4",
  "status": "completed",
  "progress": 100,
  "current_step": "Done! Portfolio ready.",
  "result": {
    "success": true,
    "project_id": "a1b2c3d4",
    "message": "Portfolio generated successfully!",
    "output_path": "C:\\...\\generated_sites\\a1b2c3d4",
    "zip_download_url": "/portfolio-builder/download/a1b2c3d4",
    "preview_url": "/portfolio-builder/preview/a1b2c3d4",
    "errors": [],
    "warnings": []
  }
}
```

**⚠️ NOTE:** Generation takes **2-3 minutes**. Keep polling until `status` = `completed`.

---

## Step 3: Preview the Generated Site

### In Browser (RECOMMENDED)
Once status is `completed`, open in browser:
```
http://localhost:8000/portfolio-builder/preview/a1b2c3d4
```

This serves the **built React app** (from `dist/` folder after `npm run build`).

**Note:** The preview is a fully working React app:
- Hero section with your name
- About, Skills, Experience, Projects, Contact sections
- All styled with your requested colors

### Build Process (Automatic)
During generation, the backend runs:
1. `npm install` - installs dependencies
2. `npm run build` - creates optimized production build
3. Serves `dist/index.html` for preview

### In Postman
- **Method:** `GET`
- **URL:** `http://localhost:8000/portfolio-builder/preview/a1b2c3d4`

Response will be HTML content of the built React app.

---

## Step 4: Download ZIP

### Request
- **Method:** `GET`
- **URL:** `http://localhost:8000/portfolio-builder/download/a1b2c3d4`

### Postman Setup
1. Select **GET** method
2. Enter URL with your project_id
3. Click **Send**
4. Click **Save Response** → **Save to a file**
5. Save as `portfolio_a1b2c3d4.zip`

### What's in the ZIP?
A complete React + Tailwind project:
```
portfolio/
├── src/
│   ├── components/   # Hero, About, Skills, etc.
│   ├── App.jsx
│   └── index.css     # Tailwind styles
├── package.json
├── vite.config.js
└── index.html
```

To run locally:
```bash
unzip portfolio_a1b2c3d4.zip
cd portfolio
npm install
npm run dev
```

---

## Step 5: Cleanup (Optional)

### Request
- **Method:** `DELETE`
- **URL:** `http://localhost:8000/portfolio-builder/cleanup/a1b2c3d4`

This removes uploaded files, ZIP, and preview data to free storage.

---

## Quick Test Sequence

```
1. POST /portfolio-builder/generate         → Get project_id
2. GET  /portfolio-builder/status/{id}      → Poll until progress=100
3. Open /portfolio-builder/preview/{id}     → See preview in browser
4. GET  /portfolio-builder/download/{id}    → Download ZIP
5. DELETE /portfolio-builder/cleanup/{id}   → Clean up (optional)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Make sure venv is activated |
| Connection refused | Start server: `python main.py` |
| 404 Project not found | Check project_id is correct (no curly braces!) |
| Status stuck at 10% | Wait 2-3 minutes, generation is running |
| Preview empty | Check if status is `completed` first |
