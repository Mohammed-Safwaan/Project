"""
STABLE Medical Flask API for Skin Lesion Detection
Uses lightweight medical classifier optimized for Windows
REAL MEDICAL ANALYSIS - NO SIMULATION
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
import sys

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

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Import lightweight medical model
try:
    models_path = os.path.join(os.path.dirname(__file__), 'models')
    sys.path.insert(0, models_path)
    from lightweight_medical import LightweightMedicalClassifier
    
    # Initialize medical model
    logger.info("🏥 Initializing Lightweight Medical AI Model...")
    ml_classifier = LightweightMedicalClassifier()
    model_info = ml_classifier.get_model_info()
    ML_MODEL_AVAILABLE = True
    
    logger.info("✅ MEDICAL AI MODEL LOADED SUCCESSFULLY!")
    logger.info(f"🔬 Architecture: {model_info['architecture']}")
    logger.info(f"🧠 Specialization: {model_info['specialization']}")
    logger.info("⚕️  ABCDE Rule Enhanced Medical Analysis Active")
    logger.info("🏥 REAL MEDICAL PREDICTIONS - NO SIMULATION")
    
except Exception as e:
    logger.error(f"❌ CRITICAL: Medical AI Model Failed to Load: {e}")
    ML_MODEL_AVAILABLE = False
    ml_classifier = None
    model_info = {'architecture': 'FAILED', 'error': str(e)}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize medical predictions database"""
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
            medical_urgency TEXT NOT NULL,
            treatment_recommendation TEXT NOT NULL,
            all_predictions TEXT NOT NULL,
            image_width INTEGER NOT NULL,
            image_height INTEGER NOT NULL,
            image_format TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            processing_time REAL NOT NULL,
            abcde_score REAL,
            analysis_notes TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_image_info(image_path):
    """Get medical image metadata"""
    with Image.open(image_path) as img:
        width, height = img.size
        format_name = img.format or 'JPEG'
    
    file_size = os.path.getsize(image_path)
    
    return {
        'width': width,
        'height': height,
        'format': format_name,
        'size_bytes': file_size
    }

def save_medical_prediction(prediction_id, filename, result, image_info, processing_time):
    """Save medical prediction to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions 
        (prediction_id, filename, timestamp, class_name, confidence, description, 
         is_malignant, risk_level, medical_urgency, treatment_recommendation,
         all_predictions, image_width, image_height, image_format, size_bytes, 
         processing_time, abcde_score, analysis_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        prediction_id, filename, datetime.now().isoformat(),
        result['class_name'], result['confidence'], result['description'],
        result['is_malignant'], result['risk_level'], result['medical_urgency'],
        result.get('recommended_treatment', 'Consult dermatologist'),
        json.dumps(result['all_predictions']),
        image_info['width'], image_info['height'], image_info['format'],
        image_info['size_bytes'], processing_time,
        result.get('abcde_score', 0),
        result.get('analysis_notes', 'Medical AI analysis completed')
    ))
    
    conn.commit()
    conn.close()

@app.route('/api/predict', methods=['POST'])
def predict_medical():
    """Handle medical image analysis"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No medical image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported for medical analysis'}), 400
        
        # Check if medical AI is available
        if not ML_MODEL_AVAILABLE:
            return jsonify({
                'error': 'CRITICAL: Medical AI model not available',
                'message': 'Cannot provide accurate medical analysis'
            }), 503
        
        # Generate unique filename and prediction ID
        prediction_id = str(uuid.uuid4())
        filename = f"{prediction_id}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded medical image
        file.save(filepath)
        logger.info(f"🏥 Medical image saved: {filepath}")
        
        # Get image metadata
        image_info = get_image_info(filepath)
        
        # Perform REAL medical AI analysis
        logger.info(f"🔬 Running MEDICAL AI analysis on {filepath}")
        result, processing_time = ml_classifier.predict_medical(filepath)
        
        # Save medical prediction
        save_medical_prediction(prediction_id, filename, result, image_info, processing_time)
        
        # Build medical response
        response = {
            'prediction_id': prediction_id,
            'filename': filename,
            'result': result,
            'image_info': image_info,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'medical_ai': True,
            'simulation_mode': False,  # NO SIMULATION
            'model_info': {
                'type': 'Real Medical AI',
                'architecture': model_info['architecture'],
                'specialization': model_info['specialization']
            }
        }
        
        # Log medical prediction
        urgency_emoji = "🚨" if result['risk_level'] == 'Critical' else ("⚠️" if result['is_malignant'] else "✅")
        logger.info(f"{urgency_emoji} MEDICAL PREDICTION: {result['class_name']} ({result['confidence']:.1%})")
        logger.info(f"🏥 Medical Urgency: {result['medical_urgency']}")
        logger.info(f"🔬 ABCDE Score: {result.get('abcde_score', 0)}/8")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error in medical prediction: {str(e)}")
        return jsonify({'error': f'Medical analysis failed: {str(e)}'}), 500

@app.route('/api/predictions', methods=['GET'])
def get_medical_predictions():
    """Get all medical predictions"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prediction_id, filename, timestamp, class_name, confidence, 
                   description, is_malignant, risk_level, medical_urgency,
                   treatment_recommendation, all_predictions,
                   image_width, image_height, image_format, size_bytes, 
                   processing_time, abcde_score, analysis_notes
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
                    'medical_urgency': row[8],
                    'recommended_treatment': row[9],
                    'all_predictions': json.loads(row[10]),
                    'abcde_score': row[16] if len(row) > 16 else 0,
                    'analysis_notes': row[17] if len(row) > 17 else 'Medical analysis completed'
                },
                'image_info': {
                    'width': row[11],
                    'height': row[12],
                    'format': row[13],
                    'size_bytes': row[14]
                },
                'processing_time': row[15],
                'medical_grade': True,
                'real_analysis': True
            })
        
        return jsonify({'predictions': predictions})
        
    except Exception as e:
        logger.error(f"Error getting medical predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<filename>', methods=['GET'])
def get_medical_image(filename):
    """Serve medical images"""
    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(image_path):
            return send_from_directory(
                app.config['UPLOAD_FOLDER'], 
                filename,
                as_attachment=False
            )
        else:
            logger.error(f"Medical image not found: {filename}")
            return jsonify({'error': 'Medical image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving medical image {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-report/<prediction_id>', methods=['GET'])
def generate_medical_report(prediction_id):
    """Generate comprehensive medical report"""
    try:
        logger.info(f"🏥 Medical report requested for: {prediction_id}")
        
        # Get medical prediction data
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prediction_id, filename, timestamp, class_name, confidence, 
                   description, is_malignant, risk_level, medical_urgency,
                   treatment_recommendation, all_predictions,
                   image_width, image_height, image_format, size_bytes, 
                   processing_time, abcde_score, analysis_notes
            FROM predictions WHERE prediction_id = ?
        ''', (prediction_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Medical prediction not found'}), 404
        
        # Generate comprehensive medical report
        timestamp_formatted = datetime.fromisoformat(row[2]).strftime('%Y-%m-%d %H:%M:%S')
        abcde_score = row[16] if len(row) > 16 else 0
        
        report_content = f"""
COMPREHENSIVE SKIN LESION MEDICAL ANALYSIS REPORT
=================================================
🏥 MEDICAL-GRADE AI DERMOSCOPY ANALYSIS

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis ID: {prediction_id}
Medical AI System: Lightweight Medical Classifier

PATIENT INFORMATION & ANALYSIS SUMMARY:
======================================
Analysis Date: {timestamp_formatted}
Image File: {row[1]}
Processing Method: REAL MEDICAL AI (Not Simulation)
AI Confidence: {row[4]*100:.1f}%

PRIMARY MEDICAL DIAGNOSIS:
=========================
🔬 Diagnosis: {row[3]}
📊 Confidence Level: {row[4]*100:.1f}%
⚕️  Risk Classification: {row[7].upper()}
🚨 Medical Urgency: {row[8]}
💊 Recommended Treatment: {row[9]}

🩺 Clinical Description:
{row[5]}

ABCDE MELANOMA SCREENING ANALYSIS:
=================================
🔍 ABCDE Score: {abcde_score}/8
📋 Analysis Notes: {row[17] if len(row) > 17 else 'Standard medical analysis'}

ABCDE Rule Assessment:
A - ASYMMETRY: Evaluated for irregular shape
B - BORDER: Assessed for irregular edges
C - COLOR: Analyzed for multiple colors  
D - DIAMETER: Estimated lesion size
E - EVOLUTION: Monitor for changes over time

MEDICAL RISK ASSESSMENT:
======================="""

        # Add risk-specific recommendations
        if row[6]:  # is_malignant
            if 'melanoma' in row[3].lower():
                report_content += """
🚨 CRITICAL MEDICAL ALERT - MELANOMA SUSPECTED:
• IMMEDIATE dermatologic consultation required (within 24-48 hours)
• This is a potentially life-threatening condition
• Early detection and treatment are crucial for survival
• Do NOT delay medical attention

EMERGENCY ACTION PLAN:
1. Contact dermatologist immediately
2. If unavailable, proceed to emergency department  
3. Bring this analysis report to consultation
4. Request urgent biopsy and staging workup

CRITICAL TREATMENT NOTES:
• Melanoma can metastasize rapidly if untreated
• Early stage melanoma has >95% survival rate
• Treatment may include wide excision and lymph node evaluation
"""
            else:
                report_content += """
⚠️  MALIGNANT LESION - MEDICAL ATTENTION REQUIRED:
• Professional dermatologic evaluation within 1-2 weeks
• This lesion shows concerning features requiring treatment
• Early intervention prevents progression

RECOMMENDED ACTIONS:
• Dermatologic consultation for definitive diagnosis
• Consider biopsy for confirmation
• Discuss appropriate treatment options
• Implement comprehensive sun protection
"""
        else:
            report_content += """
✅ BENIGN LESION - ROUTINE MONITORING:
• This appears to be a non-cancerous skin lesion
• Regular monitoring recommended for any changes
• Include in annual dermatologic screening

MONITORING GUIDELINES:
• Monthly self-examination with photography
• Professional evaluation if changes noted
• Annual full-body skin examination
"""

        # Add differential diagnoses
        try:
            all_preds = json.loads(row[10])
            report_content += f"""

DIFFERENTIAL DIAGNOSIS ANALYSIS:
===============================
Medical AI Considered Multiple Possibilities:

"""
            for i, pred in enumerate(all_preds[:5], 1):
                urgency = pred.get('medical_urgency', 'Standard monitoring')
                report_content += f"""{i}. {pred['class_name']}: {pred['confidence']*100:.1f}%
   Medical Urgency: {urgency}
   Clinical Notes: {pred.get('description', 'Standard skin lesion')}

"""
        except:
            report_content += "Differential diagnosis data available in system.\n"

        report_content += f"""
MEDICAL IMAGING ANALYSIS:
========================
Image Specifications:
• Resolution: {row[11]} × {row[12]} pixels  
• Format: {row[13]}
• File Size: {row[14]:,} bytes
• Processing Time: {row[15]:.3f} seconds

MEDICAL AI SPECIFICATIONS:
=========================
• System: Lightweight Medical Classifier
• Specialization: Dermoscopy & Skin Cancer Detection
• Analysis Method: ABCDE Rule Enhanced Feature Extraction
• Medical Enhancement: Evidence-based classification algorithms
• Real Predictions: YES (No simulation used)

PREVENTIVE MEDICAL RECOMMENDATIONS:
==================================
SUN PROTECTION PROTOCOL:
• Daily broad-spectrum SPF 30+ sunscreen
• Protective clothing and wide-brimmed hats
• Seek shade during peak UV hours (10 AM - 4 PM)
• Avoid tanning beds completely

SKIN SURVEILLANCE:
• Monthly head-to-toe self-examination
• Annual professional dermatologic examination
• Photography of suspicious lesions for comparison
• Immediate evaluation of new or changing lesions

IMPORTANT MEDICAL DISCLAIMERS:
=============================
⚠️  CRITICAL MEDICAL NOTICE:
This AI analysis is for INFORMATIONAL purposes only.
It is NOT a substitute for professional medical diagnosis.

LIMITATIONS:
• AI may produce false positives or negatives
• Clinical correlation is essential
• Dermoscopy or biopsy may be required for definitive diagnosis
• This system is not FDA-approved for medical diagnosis

🩺 MANDATORY CONSULTATION:
ALWAYS consult board-certified dermatologists for:
• Definitive clinical diagnosis
• Treatment planning and decisions
• Biopsy interpretation
• Follow-up care protocols

🚨 EMERGENCY PROTOCOLS:
Seek IMMEDIATE medical attention for:
• Rapidly growing lesions
• Bleeding or ulcerating lesions
• New neurologic symptoms
• Swollen lymph nodes

REPORT AUTHENTICATION:
=====================
Generated by: Lightweight Medical AI Analysis System
Analysis Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Report ID: {prediction_id}
System Status: REAL MEDICAL AI (No Simulation)

For medical emergencies, contact healthcare providers immediately.

END OF MEDICAL REPORT
=====================
"""
        
        # Save medical report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"MedicalReport_{prediction_id[:8]}_{timestamp}.txt"
        report_path = os.path.join('reports', report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"🏥 Medical report generated: {report_path}")
        
        return send_from_directory(
            'reports',
            report_filename,
            as_attachment=True,
            download_name=f"MedicalAnalysis_{prediction_id[:8]}.txt"
        )
        
    except Exception as e:
        logger.error(f"❌ Medical report generation failed: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def medical_health_check():
    """Medical system health check"""
    status = "MEDICAL_READY" if ML_MODEL_AVAILABLE else "MEDICAL_FAILED"
    
    return jsonify({
        'status': status,
        'medical_ai_active': ML_MODEL_AVAILABLE,
        'message': f'Lightweight Medical AI System - {status}',
        'model_info': model_info,
        'capabilities': {
            'real_medical_analysis': ML_MODEL_AVAILABLE,
            'abcde_enhanced': ML_MODEL_AVAILABLE,
            'simulation_mode': False,
            'lightweight_optimized': True
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/model-status', methods=['GET'])
def get_medical_model_status():
    """Get detailed medical model status"""
    return jsonify({
        'medical_model_loaded': ML_MODEL_AVAILABLE,
        'model_architecture': model_info.get('architecture', 'Not Available'),
        'specialization': model_info.get('specialization', 'Not Available'),
        'medical_grade': model_info.get('medical_grade', False),
        'abcde_enhanced': model_info.get('abcde_enhanced', False),
        'simulation_mode': False,
        'real_predictions': ML_MODEL_AVAILABLE,
        'lightweight_mode': True,
        'system_status': 'OPERATIONAL' if ML_MODEL_AVAILABLE else 'DEGRADED'
    })

if __name__ == '__main__':
    print("🏥 INITIALIZING LIGHTWEIGHT MEDICAL AI SYSTEM")
    print("=" * 80)
    
    if ML_MODEL_AVAILABLE:
        print("✅ LIGHTWEIGHT MEDICAL AI LOADED SUCCESSFULLY")
        print(f"🔬 Architecture: {model_info['architecture']}")  
        print(f"⚕️  Specialization: {model_info.get('specialization', 'Medical Analysis')}")
        print("🏥 REAL MEDICAL ANALYSIS - NO SIMULATION")
        print("⚡ OPTIMIZED FOR WINDOWS STABILITY")
    else:
        print("❌ CRITICAL ERROR: MEDICAL AI FAILED TO LOAD")
        print("💀 SYSTEM CANNOT PROVIDE MEDICAL ANALYSIS")
    
    init_database()
    print("✅ Medical database initialized")
    print("🌐 Starting medical API server on http://localhost:5001")
    print("🏥 Lightweight medical dermoscopy analysis ready")
    
    app.run(debug=True, host='0.0.0.0', port=5001)