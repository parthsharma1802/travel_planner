# Environment & Infrastructure Report

## System Information
- **OS**: macOS 26.5.2 (Build 25F84)
- **Architecture**: Apple Silicon arm64 (M4, 16 GB RAM)
- **Disk Usage**: Total: 228.27 GB | Used: 216.51 GB | Free: 11.77 GB

## Verification Results (16/16 Components)

| # | Component | Installed Version / Status | Health | Status |
|---|---|---|---|---|
| 1 | Python | 3.9.6 | OK | ✅ |
| 2 | PyTorch | 2.8.0 | OK | ✅ |
| 3 | Torchvision | 0.23.0 | OK | ✅ |
| 4 | OpenCV | 5.0.0 | OK | ✅ |
| 5 | NumPy | 2.0.2 | OK | ✅ |
| 6 | Pandas | 2.3.3 | OK | ✅ |
| 7 | Scikit-learn | 1.6.1 | OK | ✅ |
| 8 | Pillow | 11.3.0 | OK | ✅ |
| 9 | Plotly | 7.0.0 | OK | ✅ |
| 10 | FastAPI | 0.128.8 | OK | ✅ |
| 11 | FAISS | 1.13.0 | OK | ✅ |
| 12 | MPS | MPS Available | OK | ✅ |
| 13 | Node | v24.15.0 | OK | ✅ |
| 14 | React/Vite | Vite + React 19.2 | Scaffolded & Verified | ✅ |
| 15 | Leaflet | Leaflet & React-Leaflet | Installed | ✅ |
| 16 | Recharts | Recharts 2.x | Installed | ✅ |

## Pretrained Model Weights Availability
- ✅ resnet18_imagenet.pth (44.67 MB)
- ✅ resnet18_places365.pth (43.40 MB)
- ✅ feature_extractor_resnet18.pth (42.71 MB)

## Compatibility Notes
- **Apple Silicon (MPS)**: PyTorch 2.8.0 native ARM64 with Metal Performance Shaders enabled.
- **FAISS**: `faiss-cpu` 1.13.0 compiled for macOS ARM64.
- **OpenCV**: `opencv-python` 5.0.0.93 native build.
- **Frontend**: React 19.2 + Vite 8.2 with Tailwind CSS v4, Lucide React, Recharts, and Leaflet.

## Reproduction Commands
```bash
# 1. Environment Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Download Pretrained Weights
python scripts/download_pretrained_models.py

# 3. Test MPS
python scripts/test_mps.py

# 4. Frontend Build & Dev
cd frontend && npm install && npm run dev
```
