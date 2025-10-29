"""
Flask API server for Skin Lesion Detection with Real ML Model
Includes DenseNet201 model inference and PDF report generation
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
import traceback

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import ML model and utilities
try:
    from models.skin_classifier import SkinLesionClassifier
    ML_IMPORT_SUCCESS = True
    logger.info("✓ ML Model module imported successfully")
except Exception as import_error:
    logger.warning(f"Could not import ML model: {str(import_error)}")
    ML_IMPORT_SUCCESS = False
    SkinLesionClassifier = None

from utils.pdf_generator import create_report

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
DATABASE_FILE = 'predictions.db'
MODEL_WEIGHTS_PATH = 'models/best_model_weights.h5'  # Path to trained model weights
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Initialize ML Model
ml_model = None
MODEL_LOADED = False

if ML_IMPORT_SUCCESS and SkinLesionClassifier:
    try:
        logger.info("Initializing Skin Lesion Classifier...")
        if os.path.exists(MODEL_WEIGHTS_PATH):
            ml_model = SkinLesionClassifier(model_path=MODEL_WEIGHTS_PATH)
            MODEL_LOADED = True
            logger.info("✓ ML Model loaded successfully with trained weights!")
        else:
            logger.warning(f"Model weights not found at {MODEL_WEIGHTS_PATH}")
            ml_model = SkinLesionClassifier()  # Initialize without weights
            logger.info("✓ ML Model initialized (without trained weights - using base architecture)")
    except Exception as e:
        logger.error(f"✗ Failed to initialize ML model: {str(e)}")
        logger.error(traceback.format_exc())
else:
    logger.error("✗ ML Model could not be imported - running without ML capabilities")

# Database initialization
def init_database():
    """Initialize SQLite database with updated schema"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT,
            class_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT NOT NULL,
            is_malignant BOOLEAN NOT NULL,
            description TEXT,
            all_predictions TEXT,
            image_width INTEGER,
            image_height INTEGER,
            image_format TEXT,
            image_size_bytes INTEGER,
            processing_time REAL,
            pdf_report_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Initialize database on startup
init_database()

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_info(image_path):
    """Extract image metadata"""
    try:
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'size_bytes': os.path.getsize(image_path)
            }
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return {'width': 0, 'height': 0, 'format': 'unknown', 'size_bytes': 0}

def save_prediction_to_db(prediction_id, filename, original_filename, result, image_info, processing_time, pdf_path=None):
    """Save prediction result to database"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions (
                prediction_id, filename, original_filename, class_name, confidence,
                risk_level, is_malignant, description, all_predictions,
                image_width, image_height, image_format, image_size_bytes,
                processing_time, pdf_report_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_id,
            filename,
            original_filename,
            result['class_name'],
            result['confidence'],
            result['risk_level'],
            result['is_malignant'],
            result['description'],
            json.dumps(result.get('all_predictions', [])),
            image_info['width'],
            image_info['height'],
            image_info['format'],
            image_info['size_bytes'],
            processing_time,
            pdf_path
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Prediction saved to database: {prediction_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL_LOADED,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Handle image upload and ML prediction"""
    start_time = time.time()
    
    try:
        # Check if ML model is available
        if ml_model is None:
            return jsonify({
                'error': 'ML model not initialized',
                'message': 'The AI model is currently unavailable. Please contact support.'
            }), 503
        
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed types: PNG, JPG, JPEG, BMP, TIFF'}), 400
        
        # Generate unique filename
        original_filename = file.filename
        prediction_id = str(uuid.uuid4())
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{prediction_id}_{int(time.time())}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save uploaded file
        file.save(file_path)
        logger.info(f"Image saved: {unique_filename}")
        
        # Get image information
        image_info = get_image_info(file_path)
        
        # Perform ML prediction
        logger.info("Running ML prediction...")
        ml_result = ml_model.predict(file_path)
        
        processing_time = time.time() - start_time
        
        # Prepare result data
        result = {
            'class_name': ml_result['class_name'],
            'confidence': float(ml_result['confidence']),
            'description': ml_result['description'],
            'is_malignant': ml_result['is_malignant'],
            'risk_level': ml_result['risk_level'],
            'all_predictions': [
                {
                    'class_name': class_name,
                    'confidence': float(confidence),
                    'description': ml_model.risk_classification.get(
                        list(ml_model.class_names.keys())[list(ml_model.class_names.values()).index(class_name)],
                        {}
                    ).get('description', '')
                }
                for class_name, confidence in sorted(
                    ml_result['all_probabilities'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ]
        }
        
        # Generate PDF report
        logger.info("Generating PDF report...")
        try:
            prediction_data = {
                'prediction_id': prediction_id,
                'filename': unique_filename,
                'result': result,
                'processing_time': processing_time
            }
            pdf_path = create_report(prediction_data, file_path, output_dir=REPORTS_FOLDER)
            logger.info(f"PDF report generated: {pdf_path}")
        except Exception as pdf_error:
            logger.error(f"Error generating PDF: {str(pdf_error)}")
            pdf_path = None
        
        # Save to database
        save_prediction_to_db(
            prediction_id,
            unique_filename,
            original_filename,
            result,
            image_info,
            processing_time,
            pdf_path
        )
        
        # Prepare response
        response = {
            'success': True,
            'prediction_id': prediction_id,
            'filename': unique_filename,
            'result': result,
            'image_info': image_info,
            'processing_time': round(processing_time, 3),
            'pdf_available': pdf_path is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Prediction completed: {result['class_name']} ({result['confidence']:.2%})")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get all predictions history"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM predictions 
            ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append({
                'prediction_id': row['prediction_id'],
                'filename': row['filename'],
                'original_filename': row['original_filename'],
                'result': {
                    'class_name': row['class_name'],
                    'confidence': row['confidence'],
                    'risk_level': row['risk_level'],
                    'is_malignant': bool(row['is_malignant']),
                    'description': row['description'],
                    'all_predictions': json.loads(row['all_predictions']) if row['all_predictions'] else []
                },
                'image_info': {
                    'width': row['image_width'],
                    'height': row['image_height'],
                    'format': row['image_format'],
                    'size_bytes': row['image_size_bytes']
                },
                'processing_time': row['processing_time'],
                'pdf_available': row['pdf_report_path'] is not None,
                'timestamp': row['timestamp']
            })
        
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': predictions
        })
        
    except Exception as e:
        logger.error(f"Error fetching predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """Get specific prediction by ID"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM predictions WHERE prediction_id = ?', (prediction_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Prediction not found'}), 404
        
        prediction = {
            'prediction_id': row['prediction_id'],
            'filename': row['filename'],
            'original_filename': row['original_filename'],
            'result': {
                'class_name': row['class_name'],
                'confidence': row['confidence'],
                'risk_level': row['risk_level'],
                'is_malignant': bool(row['is_malignant']),
                'description': row['description'],
                'all_predictions': json.loads(row['all_predictions']) if row['all_predictions'] else []
            },
            'image_info': {
                'width': row['image_width'],
                'height': row['image_height'],
                'format': row['image_format'],
                'size_bytes': row['image_size_bytes']
            },
            'processing_time': row['processing_time'],
            'pdf_available': row['pdf_report_path'] is not None,
            'timestamp': row['timestamp']
        }
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error fetching prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/<prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    """Delete a prediction"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Get file info before deleting
        cursor.execute('SELECT filename, pdf_report_path FROM predictions WHERE prediction_id = ?', (prediction_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Prediction not found'}), 404
        
        filename, pdf_path = row
        
        # Delete from database
        cursor.execute('DELETE FROM predictions WHERE prediction_id = ?', (prediction_id,))
        conn.commit()
        conn.close()
        
        # Delete associated files
        try:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as file_error:
            logger.warning(f"Error deleting files: {str(file_error)}")
        
        return jsonify({'success': True, 'message': 'Prediction deleted'})
        
    except Exception as e:
        logger.error(f"Error deleting prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<filename>', methods=['GET'])
def get_image(filename):
    """Serve uploaded image"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404

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

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get analysis statistics"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total_analyses = cursor.fetchone()[0]
        
        # Malignant vs Benign
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE is_malignant = 1')
        malignant_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE is_malignant = 0')
        benign_count = cursor.fetchone()[0]
        
        # Most common conditions
        cursor.execute('''
            SELECT class_name, COUNT(*) as count 
            FROM predictions 
            GROUP BY class_name 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        common_conditions = [{'class_name': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Average confidence
        cursor.execute('SELECT AVG(confidence) FROM predictions')
        avg_confidence = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'total_analyses': total_analyses,
            'malignant_count': malignant_count,
            'benign_count': benign_count,
            'common_conditions': common_conditions,
            'average_confidence': round(avg_confidence, 4)
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Skin Lesion Detection API Server")
    logger.info("=" * 60)
    logger.info(f"Model Status: {'Loaded' if MODEL_LOADED else 'Not Loaded'}")
    logger.info(f"Upload Folder: {UPLOAD_FOLDER}")
    logger.info(f"Reports Folder: {REPORTS_FOLDER}")
    logger.info(f"Database: {DATABASE_FILE}")
    logger.info("=" * 60)
    logger.info("Starting server on http://localhost:5000")
    logger.info("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
