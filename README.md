# AI Assignment Platform (Python-Only)

Minimal working prototype you can run in **PyCharm**.

## Features
- Role-based login (student/faculty) — demo users are seeded
- Upload PDF/DOCX (student)
- Faculty dashboard to view, grade, approve/reject
- AI similarity (TF-IDF + Cosine; optional Sentence-BERT)
- PDF report generation with color-coded similarities
- MongoDB via PyMongo

## Quick Start

1) Create virtual env and install requirements
```bash
pip install -r requirements.txt
```

2) Copy `.env.example` to `.env` and adjust if needed
```bash
cp .env.example .env
```

3) Ensure MongoDB running locally or set MONGO_URI to Atlas
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_assignment_platform
```

4) Run
```bash
python app.py
```
Open http://127.0.0.1:5000

### Demo Credentials
- Student: `student1@example.com` / `student123`
- Faculty: `faculty1@example.com` / `faculty123`

## Notes
- Uploads saved in `uploads/`
- Reports in `reports/generated_reports/`
- Toggle sentence-transformers by setting `USE_EMBEDDINGS=true` in `.env` (heavy download)