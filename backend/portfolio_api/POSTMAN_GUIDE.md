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

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/portfolio-builder/generate` | Generate from file upload |
| POST | `/portfolio-builder/generate-text` | Generate from resume text |
| GET | `/portfolio-builder/status/{project_id}` | Check generation progress |
| GET | `/portfolio-builder/preview/{project_id}` | Live preview in browser |
| GET | `/portfolio-builder/download/{project_id}` | Download ZIP file |
| DELETE | `/portfolio-builder/cleanup/{project_id}` | Clean up project files |

---

## Step 1: Generate Portfolio (File Upload)

### Request
- **Method:** `POST`
- **URL:** `http://localhost:8000/portfolio-builder/generate`
- **Body:** `form-data`

| Key | Type | Value |
|-----|------|-------|
| `resume_file` | File | Your resume (PDF, DOCX, or TXT) |
| `user_prompt` | Text | `Create a modern portfolio with yellow background and black text` |

### Postman Setup
1. Select **POST** method
2. Enter URL: `http://localhost:8000/portfolio-builder/generate`
3. Go to **Body** tab → Select **form-data**
4. Add key `resume_file` → Change type to **File** → Select your resume
5. Add key `user_prompt` → Enter your style preferences
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

**⚠️ Copy the `project_id`** - you need it for the next steps!

---

## Step 2: Check Generation Status

### Request
- **Method:** `GET`
- **URL:** `http://localhost:8000/portfolio-builder/status/{project_id}`

Replace `{project_id}` with YOUR project_id from Step 1 (e.g., `a1b2c3d4`)

### Progress Stages
| Progress | Step |
|----------|------|
| 0% | Queued for processing |
| 10-20% | Starting, parsing resume |
| 30% | Running workflow |
| 80% | Copying files |
| 85-95% | Building preview (npm install & build) |
| 100% | Done |

### Example Responses

**While processing:**
```json
{
  "project_id": "a1b2c3d4",
  "status": "processing",
  "progress": 30,
  "current_step": "Running portfolio generation workflow...",
  "result": null
}
```

**When completed:**
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

**⏱️ Note:** Generation takes **3-5 minutes** (includes npm build). Keep polling until `status` = `completed`.

---

## Step 3: Preview the Generated Site

### In Browser (RECOMMENDED)
Once status is `completed`, open in browser:
```
http://localhost:8000/portfolio-builder/preview/{project_id}
```

This serves the **built React app** from `dist/` folder.

**What you'll see:**
- Hero section with your name and title
- About, Skills, Experience, Projects, Contact sections
- All styled with your requested colors

### How It Works
During generation, the backend automatically:
1. `npm install` - installs dependencies
2. `npm run build` - creates production build
3. Serves `dist/index.html` for preview

### For Frontend iframe
```html
<iframe 
  src="http://localhost:8000/portfolio-builder/preview/{project_id}" 
  width="100%" 
  height="600"
/>
```

---

## Step 4: Download ZIP

### Request
- **Method:** `GET`
- **URL:** `http://localhost:8000/portfolio-builder/download/{project_id}`

### In Postman
1. Enter the URL with your project_id
2. Click **Send**
3. Click **Save Response** → **Save to a file**
4. Save as `portfolio_{project_id}.zip`

### ZIP Contents
```
portfolio/
├── package.json
├── vite.config.js
├── index.html
├── tailwind.config.js
├── postcss.config.js
├── src/
│   ├── components/
│   │   ├── Hero.jsx
│   │   ├── About.jsx
│   │   ├── Skills.jsx
│   │   └── ...
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
└── dist/              (if built)
    ├── index.html
    └── assets/
```

### Run Locally
```bash
unzip portfolio_{project_id}.zip
cd portfolio
npm install
npm run dev
```

---

## Step 5: Cleanup (Optional)

### Request
- **Method:** `DELETE`
- **URL:** `http://localhost:8000/portfolio-builder/cleanup/{project_id}`

Removes:
- Uploaded resume file
- Generated ZIP
- Preview build files

---

## Alternative: Generate from Text

If you have resume text instead of a file:

### Request
- **Method:** `POST`
- **URL:** `http://localhost:8000/portfolio-builder/generate-text`
- **Body:** `raw` → `JSON`

```json
{
  "user_prompt": "Create a modern portfolio with dark theme",
  "resume_text": "Ahmed Raza\nAI Engineer\n\nSkills: Python, TensorFlow, LangChain\n\nExperience:\n- AI Engineer at XYZ Company (2023-Present)"
}
```

---

## Quick Test Flow

```
1. POST /portfolio-builder/generate         → Get project_id
2. GET  /portfolio-builder/status/{id}      → Poll until progress=100
3. Open http://localhost:8000/portfolio-builder/preview/{id} in browser
4. GET  /portfolio-builder/download/{id}    → Download ZIP
5. DELETE /portfolio-builder/cleanup/{id}   → Clean up (optional)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Activate venv: `.venv\Scripts\Activate` |
| Connection refused | Start server: `python main.py` |
| 404 Project not found | Check project_id is correct (no curly braces!) |
| Status stuck at 30% | Wait 3-5 minutes, generation is running |
| Preview shows blank | Wait for status = `completed`, try without trailing slash |
| Assets not loading | Check vite.config.js has `base: './'` |
