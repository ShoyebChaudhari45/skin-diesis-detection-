Sample Test Images for Skin Disease Detection
==============================================

This folder contains sample images that can be used to test the 
skin disease detection system's prediction functionality.

HOW TO USE:
1. Start the server: python -m uvicorn backend.main:app --reload --port 8000
2. Navigate to http://localhost:8000/predict
3. Upload any of these images using the upload interface
4. Click "Analyze with AI" to get a prediction

FILES:
- sample_mole_1.png    → A skin mole sample image
- sample_lesion_2.png  → A skin lesion sample image
- sample_spot_3.png    → A pigmented spot sample image

NOTE: 
These are AI-generated sample images for testing purposes. 
The demo model uses random weights, so predictions will not be 
clinically accurate. For accurate predictions, train the model 
on the real HAM10000 dataset using: python ml_model/train.py

You can also download real dermatoscopic images from:
- Kaggle: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
- ISIC Archive: https://www.isic-archive.com/
