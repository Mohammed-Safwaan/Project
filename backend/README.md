# Skin Lesion Detection Backend

Flask-based ML backend for skin lesion classification using DenseNet201.

## Features

- 🧠 **Deep Learning Model**: DenseNet201 trained for 7-class skin lesion detection
- 📸 **Image Processing**: Automatic preprocessing and validation
- 🗄️ **SQLite Database**: Local storage for predictions and metadata
- 🔒 **Secure Upload**: File validation and secure storage
- 📊 **Statistics**: Comprehensive analytics and reporting
- 🌐 **REST API**: Full RESTful API for frontend integration

## Model Classes

The model can detect 7 types of skin lesions:

1. **Actinic keratoses** (Malignant) - Precancerous lesions
2. **Basal cell carcinoma** (Malignant) - Common skin cancer
3. **Benign keratosis-like lesions** (Benign) - Non-cancerous growths
4. **Dermatofibroma** (Benign) - Common benign tumor
5. **Melanocytic nevi** (Benign) - Common moles
6. **Melanoma** (Malignant) - Serious skin cancer
7. **Vascular lesions** (Benign) - Blood vessel abnormalities

## Setup

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

## API Endpoints

### Health & Info
- `GET /health` - Health check
- `GET /model/info` - Model information and statistics
- `GET /statistics` - Application statistics

### Predictions
- `POST /predict` - Upload image and get prediction
- `GET /predictions` - Get prediction history (with pagination)
- `GET /predictions/<id>` - Get specific prediction details
- `DELETE /predictions/<id>` - Delete prediction and image

### Images
- `GET /image/<filename>` - Serve uploaded images

### Utilities
- `POST /cleanup` - Clean up old predictions and images

## API Usage Examples

### Upload Image for Prediction
```bash
curl -X POST -F "image=@lesion.jpg" http://localhost:5000/predict
```

### Get Predictions History
```bash
curl "http://localhost:5000/predictions?limit=10&offset=0"
```

### Get Statistics
```bash
curl http://localhost:5000/statistics
```

## Response Format

### Prediction Response
```json
{
  "prediction_id": 123,
  "result": {
    "predicted_class": 5,
    "class_name": "Melanoma",
    "confidence": 0.87,
    "risk_level": "Malignant",
    "risk_color": "#dc3545",
    "description": "Serious form of skin cancer",
    "is_malignant": true,
    "all_probabilities": {
      "Actinic keratoses": 0.02,
      "Basal cell carcinoma": 0.05,
      "Benign keratosis-like lesions": 0.01,
      "Dermatofibroma": 0.02,
      "Melanocytic nevi": 0.03,
      "Melanoma": 0.87,
      "Vascular lesions": 0.00
    }
  },
  "image_info": {
    "filename": "skin_20241028_143022_abc123.jpg",
    "size": {"width": 1024, "height": 768, "mode": "RGB"},
    "file_size_bytes": 245760
  },
  "display_image_url": "/image/skin_20241028_143022_abc123_display.jpg",
  "processing_time": 1.23,
  "timestamp": "2024-10-28T14:30:22.123456"
}
```

## Configuration

Environment variables (`.env` file):

- `FLASK_ENV` - Flask environment (development/production)
- `DATABASE_PATH` - SQLite database file path
- `UPLOAD_FOLDER` - Image upload directory
- `MAX_CONTENT_LENGTH` - Maximum file size (bytes)
- `MODEL_PATH` - Path to model weights file
- `LOG_LEVEL` - Logging level

## File Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup.bat             # Windows setup script
├── setup.sh              # Linux/Mac setup script
├── .env                  # Environment configuration
├── models/
│   ├── skin_classifier.py # Model implementation
│   └── densenet_weights.h5 # Model weights (after training)
├── utils/
│   ├── database.py       # Database utilities
│   └── image_processing.py # Image processing utilities
├── uploads/              # Uploaded images
└── logs/                 # Log files
```

## Database Schema

### Predictions Table
- `id` - Primary key
- `image_filename` - Secure filename
- `image_path` - Full file path
- `predicted_class` - Predicted class index
- `class_name` - Human-readable class name
- `confidence` - Prediction confidence score
- `risk_level` - Malignant/Benign classification
- `description` - Class description
- `all_probabilities` - JSON of all class probabilities
- `created_at` - Timestamp
- `processing_time` - Inference time

## Logging

Logs are written to console and can be configured via `LOG_LEVEL` environment variable.

## Security Features

- File type validation
- File size limits
- Secure filename generation
- Input sanitization
- Error handling

## Performance

- Optimized image preprocessing
- Efficient database queries
- Automatic cleanup of old files
- Display image optimization

## Model Performance

Based on DenseNet201 architecture:
- **Validation Accuracy**: 86.696%
- **Test Accuracy**: 87.725%
- **Input Size**: 192x256x3
- **Parameters**: ~19.3M

## Troubleshooting

### Common Issues

1. **Model not loading**: Ensure TensorFlow is properly installed
2. **Database errors**: Check write permissions in backend directory
3. **Image upload fails**: Verify file size and format requirements
4. **CORS issues**: Frontend and backend on different ports (handled by flask-cors)

### Error Codes

- `400` - Bad request (invalid input)
- `404` - Resource not found
- `413` - File too large
- `500` - Internal server error

## Development

To add new features:

1. Update model classes in `models/skin_classifier.py`
2. Add database schema changes in `utils/database.py`
3. Create new API endpoints in `app.py`
4. Update documentation

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper logging
4. Set up database backups
5. Use HTTPS

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```