"""
Flask API server for Skin Lesion Detection with Real DenseNet201 Model
Uses TensorFlow DenseNet201 with ImageNet weights for transfer learning
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import time
import logging
from datetime import datetime
import uuid
import json
import sqlite3
from PIL import Image

# Import DenseNet model
from models.densenet_model import DenseNetSkinClassifier

# Import PDF generator
from utils.pdf_generator import create_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
DATABASE_FILE = 'predictions.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Initialize ML Model
logger.info("=" * 60)
logger.info("Initializing DenseNet201 Skin Lesion Classifier...")
logger.info("=" * 60)
ml_model = DenseNetSkinClassifier()
logger.info("=" * 60)
logger.info("✓ DenseNet201 Model initialized successfully!")
logger.info("=" * 60)

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
            processing_time REAL NOT NULL,
            pdf_report_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def real_ml_prediction(image_path):
    """Perform real ML prediction using CPU-based classifier"""
    start_time = time.time()
    
    # Get image info
    with Image.open(image_path) as img:
        width, height = img.size
        format_name = img.format or 'JPEG'
    
    file_size = os.path.getsize(image_path)
    
    # Perform real ML prediction
    ml_result = ml_model.predict(image_path)
    
    # Build all predictions list sorted by confidence
    all_predictions = []
    for class_name, confidence in sorted(
        ml_result['all_probabilities'].items(), 
        key=lambda x: x[1], 
        reverse=True
    ):
        all_predictions.append({
            'class_name': class_name,
            'confidence': confidence,
            'description': ml_model.risk_classification[
                list(ml_model.class_names.values()).index(class_name)
            ]['description']
        })
    
    result = {
        'class_name': ml_result['class_name'],
        'confidence': ml_result['confidence'],
        'description': ml_result['description'],
        'is_malignant': ml_result['is_malignant'],
        'risk_level': ml_result['risk_level'],
        'all_predictions': all_predictions
    }
    
    image_info = {
        'width': width,
        'height': height,
        'format': format_name,
        'size_bytes': file_size
    }
    
    processing_time = time.time() - start_time
    
    return result, image_info, processing_time

def save_prediction(prediction_id, filename, result, image_info, processing_time, pdf_path=None):
    """Save prediction to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions 
        (prediction_id, filename, timestamp, class_name, confidence, description, 
         is_malignant, risk_level, all_predictions, image_width, image_height, 
         image_format, size_bytes, processing_time, pdf_report_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        prediction_id, filename, datetime.now().isoformat(),
        result['class_name'], result['confidence'], result['description'],
        result['is_malignant'], result['risk_level'], 
        json.dumps(result['all_predictions']),
        image_info['width'], image_info['height'], image_info['format'],
        image_info['size_bytes'], processing_time, pdf_path
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
        
        # Perform real ML prediction
        result, image_info, processing_time = real_ml_prediction(filepath)
        
        # Generate PDF report
        logger.info("Generating PDF report...")
        pdf_path = None
        try:
            prediction_data = {
                'prediction_id': prediction_id,
                'filename': filename,
                'result': result,
                'processing_time': processing_time
            }
            pdf_path = create_report(prediction_data, filepath, output_dir=REPORTS_FOLDER)
            logger.info(f"PDF report generated: {pdf_path}")
        except Exception as pdf_error:
            logger.error(f"Error generating PDF: {str(pdf_error)}")
        
        # Save to database
        save_prediction(prediction_id, filename, result, image_info, processing_time, pdf_path)
        
        response = {
            'prediction_id': prediction_id,
            'filename': filename,
            'result': result,
            'image_info': image_info,
            'processing_time': processing_time,
            'pdf_available': pdf_path is not None,
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
                   image_width, image_height, image_format, size_bytes, processing_time, pdf_report_path
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
                'processing_time': row[13],
                'pdf_available': row[14] is not None
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

@app.route('/api/report/<prediction_id>', methods=['GET'])
def download_report(prediction_id):
    """Download PDF report for a prediction"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT pdf_report_path, class_name FROM predictions WHERE prediction_id = ?', (prediction_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Prediction not found'}), 404
        
        pdf_path, class_name = row
        
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF report not available'}), 404
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'skin_lesion_report_{class_name.replace(" ", "_")}_{prediction_id[:8]}.pdf'
        )
        
    except Exception as e:
        logger.error(f"Error serving PDF report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Skin Lesion Detection API with DenseNet201',
        'model_type': 'DenseNet201 with ImageNet transfer learning',
        'framework': 'TensorFlow',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Skin Lesion Detection API - DenseNet201 Model")
    print("=" * 60)
    init_database()
    print("✓ Database initialized successfully")
    model_info = ml_model.get_model_summary()
    if model_info:
        print(f"✓ Model: {model_info['model_type']}")
        print(f"✓ Framework: {model_info['framework']}")
        print(f"✓ Device: {model_info['device']}")
        print(f"✓ Parameters: {model_info['total_params']:,}")
    print("=" * 60)
    print("Starting Flask server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)