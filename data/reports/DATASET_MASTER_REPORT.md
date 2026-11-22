# DATASET MASTER AUDIT REPORT

**AI-Powered Visual Travel Recommendation System — Phase 2 Audit**

## A. Dataset Inventory

| Dataset Name | Type | File Size | Items / Rows | Classes | Purpose |
|---|---|---:|---:|---:|---|
| Indian Monument Dataset | Image Folder (ZIP) | 620.56 MB | 4718 images | 26 | Landmark Recognition & Vision |
| India Tourism JSON | JSON Metadata | 0.12 MB | 340+ records | N/A | Travel Recommendation Engine |
| State-Wise Tourism Dataset | 32 Excel Spreadsheets | 2.99 MB | 4,143 destinations (17.2M reviews) | 32 States/UTs | Destination Attributes, Ratings, GPS, Categories |
| Image DB Archive | ZIP Archive | 4096.00 MB | 0 (Corrupted) | N/A | Skipped due to BadZip signature |


## B. Image Quality & Dimension Statistics

- **Total Images Audited**: 4718
- **Valid Readable Images**: 4718
- **Corrupt / Zero-Byte Images**: 0
- **Exact Duplicates (SHA-256)**: 2047
- **Near Duplicates (Perceptual Hash)**: 45
- **Min Dimension**: 100 x 88 px
- **Max Dimension**: 6016 x 7304 px
- **Average Resolution**: 635 x 506 px

## C. Class Distribution Summary (Indian Monuments)

- **Total Classes**: 26
- **Min Class Size**: 23 images (lotus_temple)
- **Max Class Size**: 432 images (qutub_minar)
- **Average Images / Class**: 181.5
- **Class Imbalance Ratio (Max/Min)**: 18.78x

## D. Destination Mapping Summary

- **Total CV Landmark Classes**: 26
- **Successfully Mapped to Tourism Database (≥80% confidence)**: 21 (80.8%)
- Mapping CSV generated at: `data/reports/destination_mapping.csv`

## E. Problems Discovered

1. **Corrupted Zip Archive**: `image_db.zip` (4.0 GB) has an invalid central directory signature and could not be extracted.
2. **Exact & Near Duplicate Images**: Detected exact duplicate images via SHA-256 and near-duplicates via perceptual hashing.
3. **Class Imbalance**: Monument classes vary between ~30 images and 200+ images per class.
4. **Naming Discrepancies**: Minor variations between folder names (e.g. `Ajanta Caves`) and tourism database records (e.g. `Ajanta & Ellora Caves`).

## F. Recommended Solutions & Next Phase Pipeline

1. **Data Cleaning**: Remove corrupt images and filter duplicate images during preprocessing into `data/processed/`.
2. **Normalization**: Use `destination_mapping.csv` to standardize destination IDs across CV outputs and backend tourism APIs.
3. **Dataset Split**: Create stratified 70/15/15 Train/Val/Test splits preserving class proportions.
4. **Image Preprocessing**: Resize images to 224x224 and normalize with ImageNet mean/std for PyTorch ResNet-18 training.
5. **Embedding Retrieval**: Build a FAISS vector index using the pretrained 512-dim ResNet-18 feature extractor.
