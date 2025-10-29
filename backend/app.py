"""
Flask API server for Skin Lesion Detection
Provides ML inference endpoints and database integration
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import time
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import traceback

# Import our custom modules
from models.skin_classifier import SkinLesionClassifier
from utils.database import get_database_manager
from utils.image_processing import get_image_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'skin-lesion-detection-secret-key-2024'

# Global variables for model and utilities
model = None
db_manager = None
image_processor = None

def initialize_services():
    """Initialize ML model and services"""
    global model, db_manager, image_processor
    
    try:
        logger.info("Initializing services...")
        
        # Initialize model
        model_path = os.path.join('models', 'densenet_weights.h5')
        if os.path.exists(model_path):
            logger.info(f"Loading model from {model_path}")
            model = SkinLesionClassifier(model_path)
        else:
            logger.info("No pre-trained weights found, using base model")
            model = SkinLesionClassifier()
        
        # Initialize database
        db_manager = get_database_manager()
        
        # Initialize image processor
        image_processor = get_image_processor(app.config['UPLOAD_FOLDER'])
        
        logger.info("All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'services': {
            'model': model is not None,
            'database': db_manager is not None,
            'image_processor': image_processor is not None
        }
    })

@app.route('/model/info', methods=['GET'])
def get_model_info():
    """Get model information and statistics"""
    try:
        if not model:
            return jsonify({'error': 'Model not loaded'}), 500
        
        model_summary = model.get_model_summary()
        db_stats = db_manager.get_statistics()
        
        return jsonify({
            'model_info': model_summary,
            'database_stats': db_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_lesion():
    """Main prediction endpoint"""
    try:
        # Check if model is loaded
        if not model:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Record start time for processing
        start_time = time.time()
        
        # Save uploaded image
        file_data = file.read()
        image_info = image_processor.save_uploaded_image(file_data, file.filename)
        
        # Make prediction
        prediction_result = model.predict(image_info['path'])
        
        # Calculate processing time
        processing_time = time.time() - start_time
        image_info['processing_time'] = processing_time
        
        # Save to database
        prediction_id = db_manager.save_prediction(prediction_result, image_info)
        
        # Create display version of image
        display_path = image_processor.preprocess_for_display(image_info['path'])
        
        # Prepare response
        response = {
            'prediction_id': prediction_id,
            'result': prediction_result,
            'image_info': image_info,
            'display_image_url': f"/image/{os.path.basename(display_path)}",
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Prediction completed for {file.filename}: {prediction_result['class_name']} ({prediction_result['confidence']:.2%})")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/predictions', methods=['GET'])
def get_predictions():
    """Get prediction history with pagination"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        risk_level = request.args.get('risk_level', None)
        
        # Validate parameters
        limit = min(limit, 100)  # Cap at 100 records
        offset = max(offset, 0)
        
        # Get predictions from database
        if risk_level:
            predictions = db_manager.get_predictions_by_risk(risk_level)
            # Apply pagination manually for filtered results
            predictions = predictions[offset:offset + limit]
        else:
            predictions = db_manager.get_predictions_history(limit, offset)
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'limit': limit,
            'offset': offset,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction_detail(prediction_id):
    """Get detailed information about a specific prediction"""
    try:
        prediction = db_manager.get_prediction_by_id(prediction_id)
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Add display image URL if image exists
        if os.path.exists(prediction['image_path']):
            base_name, ext = os.path.splitext(prediction['image_path'])
            display_path = f"{base_name}_display{ext}"
            if os.path.exists(display_path):
                prediction['display_image_url'] = f"/image/{os.path.basename(display_path)}"
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error getting prediction detail: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/predictions/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    """Delete a prediction record and associated image"""
    try:
        # Get prediction info first
        prediction = db_manager.get_prediction_by_id(prediction_id)
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Delete image files
        if 'image_path' in prediction:
            image_processor.delete_image(prediction['image_path'])
        
        # Delete from database
        success = db_manager.delete_prediction(prediction_id)
        
        if success:
            return jsonify({
                'message': 'Prediction deleted successfully',
                'prediction_id': prediction_id
            })
        else:
            return jsonify({'error': 'Failed to delete prediction'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/image/<filename>')
def serve_image(filename):
    """Serve uploaded images"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'Image not found'}), 404
            
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get application statistics"""
    try:
        stats = db_manager.get_statistics()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<filename>', methods=['GET'])
def get_image(filename):
    """Serve uploaded images"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 404

@app.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """Clean up old predictions and images"""
    try:
        days_old = request.json.get('days_old', 30)
        
        # Clean up database records
        deleted_predictions = db_manager.cleanup_old_predictions(days_old)
        
        # Clean up old images
        deleted_images = image_processor.cleanup_old_images(days_old)
        
        return jsonify({
            'message': 'Cleanup completed',
            'deleted_predictions': deleted_predictions,
            'deleted_images': deleted_images
        })
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle not found errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        # Initialize services
        initialize_services()
        
        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        logger.info("Starting Flask server...")
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise