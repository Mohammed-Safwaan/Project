"""
Simplified Flask API server for Skin Lesion Detection (Testing Version)
Simulates ML predictions for integration testing without TensorFlow dependency
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import logging
from datetime import datetime
import uuid
import json
import sqlite3
from PIL import Image
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATABASE_FILE = 'predictions.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Skin lesion classes and descriptions
SKIN_CLASSES = {
    'Actinic keratoses': {
        'description': 'Pre-cancerous scaly, rough skin patches caused by sun damage',
        'is_malignant': True,
        'risk_level': 'High'
    },
    'Basal cell carcinoma': {
        'description': 'Most common skin cancer, typically appears as pearly bumps',
        'is_malignant': True,
        'risk_level': 'High'
    },
    'Benign keratosis-like lesions': {
        'description': 'Non-cancerous skin growths with rough, scaly appearance',
        'is_malignant': False,
        'risk_level': 'Low'
    },
    'Dermatofibroma': {
        'description': 'Common benign skin tumor, firm nodules in the skin',
        'is_malignant': False,
        'risk_level': 'Low'
    },
    'Melanoma': {
        'description': 'Serious form of skin cancer developing from pigment cells',
        'is_malignant': True,
        'risk_level': 'High'
    },
    'Melanocytic nevi': {
        'description': 'Common moles, usually benign pigmented skin lesions',
        'is_malignant': False,
        'risk_level': 'Low'
    },
    'Vascular lesions': {
        'description': 'Lesions involving blood vessels, typically benign',
        'is_malignant': False,
        'risk_level': 'Low'
    }
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize SQLite database with predictions table"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            class_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            description TEXT NOT NULL,
            is_malignant BOOLEAN NOT NULL,
            risk_level TEXT NOT NULL,
            all_predictions TEXT NOT NULL,
            image_width INTEGER NOT NULL,
            image_height INTEGER NOT NULL,
            image_format TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            processing_time REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def simulate_ml_prediction(image_path):
    """Simulate ML prediction with random but realistic results"""
    
    # Get image info
    with Image.open(image_path) as img:
        width, height = img.size
        format_name = img.format or 'JPEG'
    
    file_size = os.path.getsize(image_path)
    
    # Simulate processing time
    processing_time = random.uniform(1.5, 3.5)
    time.sleep(processing_time)
    
    # Random primary prediction
    primary_class = random.choice(list(SKIN_CLASSES.keys()))
    primary_confidence = random.uniform(0.65, 0.95)
    
    # Generate other predictions
    other_classes = [cls for cls in SKIN_CLASSES.keys() if cls != primary_class]
    random.shuffle(other_classes)
    
    all_predictions = [{
        'class_name': primary_class,
        'confidence': primary_confidence,
        'description': SKIN_CLASSES[primary_class]['description']
    }]
    
    # Add 3-4 other predictions with lower confidence
    remaining_confidence = 1.0 - primary_confidence
    for i, cls in enumerate(other_classes[:4]):
        if remaining_confidence <= 0:
            break
        confidence = random.uniform(0.05, min(0.25, remaining_confidence))
        remaining_confidence -= confidence
        all_predictions.append({
            'class_name': cls,
            'confidence': confidence,
            'description': SKIN_CLASSES[cls]['description']
        })
    
    # Sort by confidence
    all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
    
    primary_info = SKIN_CLASSES[primary_class]
    
    result = {
        'class_name': primary_class,
        'confidence': primary_confidence,
        'description': primary_info['description'],
        'is_malignant': primary_info['is_malignant'],
        'risk_level': primary_info['risk_level'],
        'all_predictions': all_predictions
    }
    
    image_info = {
        'width': width,
        'height': height,
        'format': format_name,
        'size_bytes': file_size
    }
    
    return result, image_info, processing_time

def save_prediction(prediction_id, filename, result, image_info, processing_time):
    """Save prediction to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions 
        (prediction_id, filename, timestamp, class_name, confidence, description, 
         is_malignant, risk_level, all_predictions, image_width, image_height, 
         image_format, size_bytes, processing_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        prediction_id, filename, datetime.now().isoformat(),
        result['class_name'], result['confidence'], result['description'],
        result['is_malignant'], result['risk_level'], 
        json.dumps(result['all_predictions']),
        image_info['width'], image_info['height'], image_info['format'],
        image_info['size_bytes'], processing_time
    ))
    
    conn.commit()
    conn.close()

@app.route('/api/predict', methods=['POST'])
def predict():
    """Handle image upload and prediction"""
    try:
        start_time = time.time()
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate unique filename and prediction ID
        prediction_id = str(uuid.uuid4())
        filename = f"{prediction_id}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(filepath)
        logger.info(f"Saved uploaded file: {filepath}")
        
        # Simulate ML prediction
        result, image_info, processing_time = simulate_ml_prediction(filepath)
        
        # Save to database
        save_prediction(prediction_id, filename, result, image_info, processing_time)
        
        response = {
            'prediction_id': prediction_id,
            'filename': filename,
            'result': result,
            'image_info': image_info,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Prediction completed: {prediction_id} - {result['class_name']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get all predictions"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prediction_id, filename, timestamp, class_name, confidence, 
                   description, is_malignant, risk_level, all_predictions,
                   image_width, image_height, image_format, size_bytes, processing_time
            FROM predictions ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append({
                'prediction_id': row[0],
                'filename': row[1],
                'timestamp': row[2],
                'result': {
                    'class_name': row[3],
                    'confidence': row[4],
                    'description': row[5],
                    'is_malignant': bool(row[6]),
                    'risk_level': row[7],
                    'all_predictions': json.loads(row[8])
                },
                'image_info': {
                    'width': row[9],
                    'height': row[10],
                    'format': row[11],
                    'size_bytes': row[12]
                },
                'processing_time': row[13]
            })
        
        return jsonify({'predictions': predictions})
        
    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """Get specific prediction"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prediction_id, filename, timestamp, class_name, confidence, 
                   description, is_malignant, risk_level, all_predictions,
                   image_width, image_height, image_format, size_bytes, processing_time
            FROM predictions WHERE prediction_id = ?
        ''', (prediction_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Prediction not found'}), 404
        
        prediction = {
            'prediction_id': row[0],
            'filename': row[1],
            'timestamp': row[2],
            'result': {
                'class_name': row[3],
                'confidence': row[4],
                'description': row[5],
                'is_malignant': bool(row[6]),
                'risk_level': row[7],
                'all_predictions': json.loads(row[8])
            },
            'image_info': {
                'width': row[9],
                'height': row[10],
                'format': row[11],
                'size_bytes': row[12]
            },
            'processing_time': row[13]
        }
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error getting prediction {prediction_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    """Delete a prediction and its associated image"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Get filename before deleting
        cursor.execute('SELECT filename FROM predictions WHERE prediction_id = ?', (prediction_id,))
        row = cursor.fetchone()
        
        if row:
            filename = row[0]
            # Delete from database
            cursor.execute('DELETE FROM predictions WHERE prediction_id = ?', (prediction_id,))
            
            # Delete image file if it exists
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted image file: {filepath}")
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Prediction deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting prediction {prediction_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<filename>', methods=['GET'])
def get_image(filename):
    """Serve uploaded images"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 404

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get application statistics"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Total predictions
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total = cursor.fetchone()[0]
        
        # Risk level counts
        cursor.execute('SELECT risk_level, COUNT(*) FROM predictions GROUP BY risk_level')
        risk_counts = dict(cursor.fetchall())
        
        # Recent activity (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) FROM predictions 
            WHERE datetime(timestamp) > datetime('now', '-7 days')
        ''')
        recent = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            'total_predictions': total,
            'high_risk': risk_counts.get('High', 0),
            'medium_risk': risk_counts.get('Medium', 0),
            'low_risk': risk_counts.get('Low', 0),
            'recent_activity': recent
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Skin Lesion Detection API (Testing Mode)',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Initializing Skin Lesion Detection API (Testing Mode)...")
    init_database()
    print("Database initialized successfully")
    print("Starting Flask server on http://localhost:5000")
    print("Note: This is a testing version with simulated ML predictions")
    app.run(debug=True, host='0.0.0.0', port=5000)