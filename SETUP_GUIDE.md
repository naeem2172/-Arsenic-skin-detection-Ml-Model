# Arsenic Detection ML – Full Setup Guide

Complete setup instructions for the Arsenic Detection web application, including virtual environment, dependencies, and Ollama chatbot.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Step 1: Create Virtual Environment](#step-1-create-virtual-environment)
4. [Step 2: Activate Virtual Environment](#step-2-activate-virtual-environment)
5. [Step 3: Install Requirements](#step-3-install-requirements)
6. [Step 4: Set Up Ollama (Chatbot)](#step-4-set-up-ollama-chatbot)
7. [Step 5: Configure Environment](#step-5-configure-environment)
8. [Step 6: Add ML Model (Optional)](#step-6-add-ml-model-optional)
9. [Step 7: Run the Application](#step-7-run-the-application)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python**: 3.10 or 3.11 (recommended for TensorFlow compatibility)
- **RAM**: 8GB minimum, 16GB+ recommended (for TensorFlow + Ollama)
- **Disk**: ~5GB for dependencies + model storage
- **OS**: Windows 10/11, macOS, or Linux

---

## Project Structure

```
Arsenic detection ml/
├── app.py                 # Main Flask application
├── auth.py                # User authentication (CSV)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create if missing)
├── models/                # Place your trained model here
├── data/                  # users.csv, predictions.csv
├── templates/             # HTML templates
├── static/                # CSS, JS, images
└── arsenic_awareness_chatbot/   # Ollama-powered chatbot
```

---

## Step 1: Create Virtual Environment

Open a terminal (PowerShell, CMD, or your IDE terminal) and navigate to the project folder:

```powershell
cd "c:\Users\Braincount\Desktop\Arsenic detection ml"
```

Create a virtual environment named `venv`:

```powershell
python -m venv venv
```

**On macOS/Linux:**
```bash
cd "/path/to/Arsenic detection ml"
python3 -m venv venv
```

---

## Step 2: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your prompt when activated.

---

## Step 3: Install Requirements

With the virtual environment activated:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- **Flask** – Web framework
- **TensorFlow** – ML model inference
- **Pillow** – Image processing
- **python-dotenv** – Environment variables
- **langdetect** – Language detection for chatbot
- **joblib**, **numpy** – Data handling

**Note:** TensorFlow installation may take several minutes.

---

## Step 4: Set Up Ollama (Chatbot)

The chatbot uses **Ollama** – a free, local LLM – no API key required.

### 4.1 Install Ollama

**Windows:**

1. **Option A – Direct download:**
   - Go to [https://ollama.com/download](https://ollama.com/download)
   - Download `OllamaSetup.exe`
   - Run the installer and follow the prompts

2. **Option B – PowerShell:**
   ```powershell
   irm https://ollama.com/install.ps1 | iex
   ```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 4.2 Start Ollama

- **Windows:** Ollama runs automatically after installation (check system tray).
- **macOS/Linux:** Run `ollama serve` in a separate terminal, or start it as a service.

### 4.3 Pull the Required Model

Open a new terminal and run:

```powershell
ollama pull llama3.2
```

This downloads the model (~2GB). First run may take a few minutes.

**Alternative models** (if llama3.2 is too large):
```powershell
ollama pull llama3.2:1b    # Smaller, faster
ollama pull mistral         # Alternative
```

### 4.4 Verify Ollama is Running

```powershell
ollama list
```

You should see `llama3.2` (or your chosen model) in the list.

---

## Step 5: Configure Environment

Create or edit a `.env` file in the project root:

```env
# Optional: Change in production
SECRET_KEY=your-secret-key-here

# ML model settings (if predictions seem wrong)
# ARSENIC_CLASS_INDEX=0
# ARSENIC_THRESHOLD=0.5

# Ollama chatbot (optional – defaults work for most users)
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

Copy from `.env.example` if available:
```powershell
copy arsenic_awareness_chatbot\.env.example .env
```

Then edit `.env` as needed.

---

## Step 6: Add ML Model (Optional)

For **Image Prediction** to work, place your trained model in the `models/` folder.

**Preferred model name:** `arsenic_skin_detection_advanced_model.h5`

**Supported formats:**
- `arsenic_skin_detection_advanced_model.h5`
- `arsenic_skin_detection_advanced_model.keras`
- `arsenic_skin_detection_model.h5`
- `model.h5`

**Custom path** (optional in `.env`):
```env
ARSENIC_MODEL_PATH=models/your_model.h5
```

**If predictions are wrong or inverted** (e.g. infected images show "No arsenic"):
- Default: `ARSENIC_INFECTED_CLASS=1` (index 1 = infected, matches notebook).
- If infected images give high `prob_class_0`, add to `.env`: `ARSENIC_INFECTED_CLASS=0`
- Run `python test_model.py infected.png healthy.png` to diagnose, or use `POST /api/predict-probs` (when logged in).

Without a model, the app runs but prediction will show "Model not loaded."

---

## Step 7: Run the Application

With venv activated and Ollama running:

```powershell
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

**Open in browser:** [http://localhost:5000](http://localhost:5000)

### Quick Test Checklist

1. **Dashboard** – Visit `/` – should load
2. **Register** – Create an account
3. **Login** – Sign in
4. **Prediction** – Upload an image (requires model in `models/`)
5. **Chatbot** – Ask a question (requires Ollama + `ollama pull llama3.2`)

---

## Troubleshooting

### "Ollama is not running"

- Ensure Ollama is installed and the service is running
- Run `ollama list` to verify
- Check that `ollama pull llama3.2` completed successfully

### "Model not loaded"

- Place your `.h5` or `.keras` model in `models/`
- **Run from project root:** Use `run.bat` (Windows) or `run.ps1` (PowerShell), or `python app.py` from the project folder
- **Avoid multiple instances:** Stop any other Flask/Python processes on port 5000 before starting
- Restart the app after adding the model
- Visit `/api/model-check` to verify path, file existence, and load status

### TensorFlow / pip install fails

- Use Python 3.10 or 3.11
- On Windows: `pip install tensorflow-cpu` if GPU causes issues

### Port 5000 already in use

```powershell
# Change port in app.py last line, or:
$env:FLASK_RUN_PORT=5001
python app.py
```

### Chatbot shows "Chatbot Not Available"

- Verify `arsenic_awareness_chatbot` folder exists
- Check that `langdetect` is installed: `pip install langdetect`
- Ensure Ollama is running and the model is pulled

---

## Summary – Quick Start

```powershell
# 1. Create and activate venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Ollama (from ollama.com) and pull model
ollama pull llama3.2

# 4. Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.

---

*Arsenic Detection – Ashraful Islam, Tanushree Das*
