# Smart Travel Planner - Setup Guide

## Requirements
- **macOS**: macOS 26.5+ (Apple Silicon arm64, M1/M2/M3/M4)
- **RAM**: 16 GB recommended
- **Python**: Python 3.9+
- **Node.js**: Node v18+ (tested on Node v24.15.0, npm 11.12.1)
- **Git**: Git 2.x

---

## 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 2. Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## 3. Pretrained Model Setup
Cache pretrained vision model weights (ResNet-18 ImageNet, ResNet-18 Places365, Feature Extractor):
```bash
python scripts/download_pretrained_models.py
```

---

## 4. Test Apple Silicon Hardware Acceleration (MPS)
```bash
python scripts/test_mps.py
```
Expected Output: `MPS AVAILABLE`

---

## 5. Backend Service Startup
Start the FastAPI server:
```bash
venv/bin/uvicorn backend.main:app --reload --port 8000
```
API Documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 6. Frontend Service Startup
Run the React + Vite dashboard:
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be available at: [http://localhost:5173](http://localhost:5173)

---

## 7. Verification Test Suite
To run the automated 16-point environment verification suite:
```bash
python scripts/verify_environment.py
```
View generated report at: `data/reports/environment_report.md`
