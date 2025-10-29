# Skin Lesion Detection Project

A complete web application for skin lesion analysis using deep learning.

## Features

- **Upload Images**: Upload skin lesion images for analysis
- **ML Analysis**: DenseNet201 model with 87.7% accuracy for 7-class classification
- **Results Dashboard**: Detailed analysis results with confidence scores
- **History Tracking**: View previous analysis results
- **Risk Assessment**: Automatic malignancy detection and risk classification

## Project Structure

```
├── src/app/           # Next.js frontend
│   ├── _comps/        # React components
│   ├── upload/        # Upload page
│   ├── results/       # Results page
│   └── history/       # History page
├── backend/           # Flask ML API
│   ├── models/        # ML model classes
│   ├── utils/         # Database and image processing
│   ├── uploads/       # Uploaded images storage
│   └── app.py         # Main Flask server
└── public/            # Static assets
```

## Setup Instructions

### Frontend (Next.js)

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will run on http://localhost:3000

### Backend (Flask ML API)

1. **Automatic Setup** (Windows):
```bash
# Double-click start-backend.bat
# OR run in terminal:
start-backend.bat
```

2. **Manual Setup**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py
```

The backend will run on http://localhost:5000

## API Endpoints

- `POST /api/predict` - Upload and analyze skin lesion image
- `GET /api/predictions` - Get prediction history
- `GET /api/predictions/<id>` - Get specific prediction
- `GET /api/statistics` - Get analysis statistics

## Model Information

- **Architecture**: DenseNet201 (pretrained ImageNet + custom classifier)
- **Classes**: 7 types of skin lesions
- **Accuracy**: 87.7% on validation set
- **Input**: 224x224 RGB images
- **Output**: Class probabilities + malignancy risk assessment

## Usage

1. Start both frontend and backend servers
2. Open http://localhost:3000
3. Navigate to Upload page
4. Upload a skin lesion image
5. View real-time ML analysis results
6. Check detailed results and prediction history

## Development

### Adding New Features
- Frontend components in `src/app/_comps/`
- Backend utilities in `backend/utils/`
- Model updates in `backend/models/`

### Testing
- Upload sample images from `Skin-Lesions-Detection-Deep-learning/`
- Check network tab for API responses
- Monitor backend logs for debugging

### Database
- SQLite database: `backend/predictions.db`
- Stores prediction results and image metadata
- Automatic table creation on first run