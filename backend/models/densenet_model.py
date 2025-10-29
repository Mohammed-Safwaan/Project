"""
DenseNet201 Model for Skin Lesion Classification
Uses pretrained ImageNet weights for transfer learning
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN warnings

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.densenet import DenseNet201, preprocess_input
from tensorflow.keras.optimizers import Adam
from PIL import Image
import logging

# Force CPU usage
tf.config.set_visible_devices([], 'GPU')

logger = logging.getLogger(__name__)

class DenseNetSkinClassifier:
    def __init__(self, model_path=None):
        """
        Initialize DenseNet201 Skin Lesion Classifier
        
        Args:
            model_path (str): Path to saved model weights (optional)
        """
        self.input_shape = (192, 256, 3)  # Based on training notebook
        self.num_classes = 7
        
        # Class mappings from HAM10000 dataset
        self.class_names = {
            0: 'Actinic keratoses',
            1: 'Basal cell carcinoma', 
            2: 'Benign keratosis-like lesions',
            3: 'Dermatofibroma',
            4: 'Melanocytic nevi',
            5: 'Melanoma',
            6: 'Vascular lesions'
        }
        
        # Risk classification
        self.risk_classification = {
            0: {'risk': 'Malignant', 'description': 'Precancerous lesions that may develop into skin cancer'},
            1: {'risk': 'Malignant', 'description': 'Most common type of skin cancer'},
            2: {'risk': 'Benign', 'description': 'Non-cancerous skin growths'},
            3: {'risk': 'Benign', 'description': 'Common benign skin tumor'},
            4: {'risk': 'Benign', 'description': 'Common moles, usually harmless'},
            5: {'risk': 'Malignant', 'description': 'Most serious form of skin cancer'},
            6: {'risk': 'Benign', 'description': 'Blood vessel abnormalities, typically benign'}
        }
        
        self.model = None
        self.model_loaded = False
        
        # Build or load model
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.build_model()
    
    def build_model(self):
        """Build DenseNet201 model with ImageNet weights"""
        try:
            logger.info("Building DenseNet201 model with ImageNet weights...")
            
            # Load pre-trained DenseNet201
            pre_trained_model = DenseNet201(
                input_shape=self.input_shape,
                include_top=False,
                weights='imagenet'
            )
            
            # Freeze base model layers initially
            for layer in pre_trained_model.layers:
                layer.trainable = False
            
            # Get last layer
            last_layer = pre_trained_model.get_layer('relu')
            last_output = last_layer.output
            
            # Add custom classification head
            x = layers.GlobalMaxPooling2D()(last_output)
            x = layers.Dense(512, activation='relu')(x)
            x = layers.Dropout(0.5)(x)
            x = layers.Dense(self.num_classes, activation='softmax')(x)
            
            # Create model
            self.model = keras.Model(pre_trained_model.input, x)
            
            # Compile model
            optimizer = Adam(
                learning_rate=0.0001,
                beta_1=0.9,
                beta_2=0.999,
                amsgrad=True
            )
            
            self.model.compile(
                loss='categorical_crossentropy',
                optimizer=optimizer,
                metrics=['accuracy']
            )
            
            logger.info(f"✓ DenseNet201 model built successfully!")
            logger.info(f"  Total parameters: {self.model.count_params():,}")
            logger.info(f"  Using: CPU (TensorFlow {tf.__version__})")
            
        except Exception as e:
            logger.error(f"Error building model: {str(e)}")
            raise
    
    def load_model(self, model_path):
        """Load saved model weights"""
        try:
            logger.info(f"Loading model from {model_path}")
            self.model = keras.models.load_model(model_path)
            self.model_loaded = True
            logger.info("✓ Model loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Building new model instead...")
            self.build_model()
    
    def preprocess_image(self, image_path):
        """Preprocess image for model prediction"""
        try:
            # Load and resize image
            img = Image.open(image_path)
            
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to model input size (width, height)
            img = img.resize((self.input_shape[1], self.input_shape[0]))
            
            # Convert to numpy array
            img_array = np.array(img, dtype=np.float32)
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            # Preprocess using DenseNet preprocessing
            img_array = preprocess_input(img_array)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def predict(self, image_path):
        """Make prediction on skin lesion image"""
        try:
            if self.model is None:
                raise ValueError("Model not initialized")
            
            logger.info(f"Analyzing image with DenseNet201: {os.path.basename(image_path)}")
            
            # Preprocess image
            preprocessed_img = self.preprocess_image(image_path)
            
            # Make prediction
            predictions = self.model.predict(preprocessed_img, verbose=0)
            probabilities = predictions[0]
            
            # Get predicted class
            predicted_class = np.argmax(probabilities)
            confidence = float(probabilities[predicted_class])
            
            # Get class information
            class_name = self.class_names[predicted_class]
            risk_info = self.risk_classification[predicted_class]
            
            # Create result
            result = {
                'predicted_class': int(predicted_class),
                'class_name': class_name,
                'confidence': confidence,
                'risk_level': risk_info['risk'],
                'description': risk_info['description'],
                'all_probabilities': {
                    self.class_names[i]: float(prob)
                    for i, prob in enumerate(probabilities)
                },
                'is_malignant': risk_info['risk'] == 'Malignant'
            }
            
            logger.info(f"  Prediction: {class_name} ({confidence:.2%} confidence)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def get_model_summary(self):
        """Get model information"""
        if self.model:
            return {
                'model_type': 'DenseNet201 with ImageNet weights',
                'total_params': self.model.count_params(),
                'input_shape': self.input_shape,
                'num_classes': self.num_classes,
                'class_names': list(self.class_names.values()),
                'framework': f'TensorFlow {tf.__version__}',
                'device': 'CPU'
            }
        return None

def create_model(model_path=None):
    """Create and return a DenseNetSkinClassifier instance"""
    return DenseNetSkinClassifier(model_path)
