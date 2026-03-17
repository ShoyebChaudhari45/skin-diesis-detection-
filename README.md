# AI-Based Skin Disease Detection Web Application

A complete ME-level project using CNN-based image classification, FastAPI backend, MongoDB database, and a modern responsive frontend with dark mode support.

## 🔬 Features

- **AI Prediction** — CNN model classifies skin images into 7 disease categories
- **JWT Authentication** — Secure signup/login with bcrypt password hashing
- **Prediction History** — Track all past predictions with images and dates
- **Admin Panel** — View users, prediction logs, and system statistics
- **Dark Mode** — Toggle between light and dark themes
- **Skincare Chatbot** — Built-in assistant for skin health tips
- **Academic Report** — Complete HTML report with diagrams

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI |
| Database | MongoDB (PyMongo) |
| ML | TensorFlow/Keras (CNN) |
| Frontend | HTML, CSS, JavaScript |
| Auth | JWT + bcrypt |

## 📦 Setup Instructions

### Prerequisites

- **Python 3.9+**
- **MongoDB** (local or [MongoDB Atlas](https://www.mongodb.com/atlas))
- **pip** (Python package manager)

### Step 1: Clone / Navigate to Project

```bash
cd "d:\Kodeneurons Projects\skin dieasis detaction"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and set your MongoDB URI:
```env
MONGODB_URI=mongodb://localhost:27017
JWT_SECRET=your-secret-key-here
```

### Step 5: Create Demo ML Model

```bash
python ml_model/create_demo_model.py
```

This creates a functional model with the correct architecture (random weights for demo).

### Step 6: Start the Server

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

### Step 7: Open the Application

Navigate to **http://localhost:8000** in your browser.

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings
│   ├── routes/
│   │   ├── auth.py          # POST /api/signup, /api/login
│   │   ├── prediction.py    # POST /api/predict, GET /api/history
│   │   └── admin.py         # GET /api/admin/*
│   └── utils/
│       ├── auth.py          # JWT + bcrypt utilities
│       ├── ml_predictor.py  # Model loading & inference
│       └── disease_info.py  # Disease database
├── frontend/
│   ├── index.html           # Login page
│   ├── signup.html          # Registration page
│   ├── dashboard.html       # Main dashboard
│   ├── predict.html         # Upload & prediction
│   ├── history.html         # Prediction history
│   ├── admin.html           # Admin panel
│   ├── css/style.css        # Design system
│   └── js/                  # JavaScript modules
├── ml_model/
│   ├── model_architecture.py  # CNN definition
│   ├── train.py               # Training pipeline
│   ├── create_demo_model.py   # Demo model creator
│   └── predict.py             # Standalone prediction
├── docs/
│   └── report.html          # Academic report
├── requirements.txt
├── .env.example
└── README.md
```

## 🧠 Training the Real Model

To train on the HAM10000 dataset:

1. Download [HAM10000](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T)
2. Place images and `HAM10000_metadata.csv` in `dataset/HAM10000/`
3. Run:

```bash
python ml_model/train.py --data_dir dataset/HAM10000 --epochs 50
```

This generates: trained model, accuracy/loss plots, and confusion matrix.

## 🎨 Disease Classes

| Disease | Code | Severity |
|---------|------|----------|
| Melanoma | mel | Critical |
| Basal Cell Carcinoma | bcc | High |
| Actinic Keratoses | akiec | Moderate |
| Benign Keratosis | bkl | Low |
| Dermatofibroma | df | Low |
| Melanocytic Nevi | nv | Low |
| Vascular Lesions | vasc | Low-Moderate |

## ⚠️ Disclaimer

This application is for **educational purposes only** and should not replace professional medical advice. Always consult a qualified dermatologist.
