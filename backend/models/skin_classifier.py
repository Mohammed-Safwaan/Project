"""
Skin Lesion Classification Model
Based on DenseNet201 architecture for 7-class skin lesion detection
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.densenet import DenseNet201
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing import image
from PIL import Image
import cv2
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkinLesionClassifier:
    def __init__(self, model_path=None):
        """
        Initialize the Skin Lesion Classifier
        
        Args:
            model_path (str): Path to saved model weights
        """
        self.input_shape = (192, 256, 3)  # Based on notebook configuration
        self.num_classes = 7
        
        # Class mappings from the dataset
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
            0: {'risk': 'Malignant', 'color': '#dc3545', 'description': 'Precancerous lesions that may develop into skin cancer'},
            1: {'risk': 'Malignant', 'color': '#dc3545', 'description': 'Type of skin cancer that begins in basal cells'},
            2: {'risk': 'Benign', 'color': '#28a745', 'description': 'Non-cancerous skin growths'},
            3: {'risk': 'Benign', 'color': '#28a745', 'description': 'Common benign skin tumor'},
            4: {'risk': 'Benign', 'color': '#28a745', 'description': 'Common moles, usually harmless'},
            5: {'risk': 'Malignant', 'color': '#dc3545', 'description': 'Serious form of skin cancer'},
            6: {'risk': 'Benign', 'color': '#28a745', 'description': 'Blood vessel abnormalities, typically benign'}
        }
        
        self.model = None
        self.model_loaded = False
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.build_model()
    
    def build_model(self):
        """Build the DenseNet201 model architecture"""
        try:
            logger.info("Building DenseNet201 model...")
            
            # Create the pre-trained model
            pre_trained_model = DenseNet201(
                input_shape=self.input_shape, 
                include_top=False, 
                weights="imagenet"
            )
            
            # Get the last layer
            last_layer = pre_trained_model.get_layer('relu')
            last_output = last_layer.output
            
            # Add custom classification layers
            x = layers.GlobalMaxPooling2D()(last_output)
            x = layers.Dense(512, activation='relu')(x)
            x = layers.Dropout(0.5)(x)
            x = layers.Dense(self.num_classes, activation='softmax')(x)
            
            # Create the model
            self.model = tf.keras.Model(pre_trained_model.input, x)
            
            # Compile the model
            optimizer = Adam(
                learning_rate=0.0001, 
                beta_1=0.9, 
                beta_2=0.999, 
                epsilon=None, 
                decay=0.0,
                amsgrad=True
            )
            
            self.model.compile(
                loss='categorical_crossentropy',
                optimizer=optimizer,
                metrics=['accuracy']
            )
            
            logger.info("Model built successfully!")
            logger.info(f"Model has {self.model.count_params():,} parameters")
            
        except Exception as e:
            logger.error(f"Error building model: {str(e)}")
            raise
    
    def load_model(self, model_path):
        """Load pre-trained model weights"""
        try:
            if not self.model:
                self.build_model()
            
            logger.info(f"Loading model weights from {model_path}")
            self.model.load_weights(model_path)
            self.model_loaded = True
            logger.info("Model weights loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def save_model(self, model_path):
        """Save model weights"""
        try:
            if self.model:
                self.model.save_weights(model_path)
                logger.info(f"Model weights saved to {model_path}")
            else:
                logger.warning("No model to save")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def preprocess_image(self, image_path_or_array):
        """
        Preprocess image for model prediction
        
        Args:
            image_path_or_array: Path to image file or numpy array
            
        Returns:
            preprocessed_image: Preprocessed image ready for prediction
        """
        try:
            # Load image
            if isinstance(image_path_or_array, str):
                img = Image.open(image_path_or_array)
            else:
                img = Image.fromarray(image_path_or_array)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to model input size
            img = img.resize((self.input_shape[1], self.input_shape[0]))  # (width, height)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Normalize pixel values to [0, 1]
            img_array = img_array.astype(np.float32) / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def predict(self, image_path_or_array):
        """
        Make prediction on skin lesion image
        
        Args:
            image_path_or_array: Path to image file or numpy array
            
        Returns:
            dict: Prediction results with confidence scores
        """
        try:
            if not self.model:
                raise ValueError("Model not loaded. Please build or load a model first.")
            
            # Preprocess image
            preprocessed_img = self.preprocess_image(image_path_or_array)
            
            # Make prediction
            predictions = self.model.predict(preprocessed_img, verbose=0)
            
            # Get prediction probabilities
            probabilities = predictions[0]
            
            # Get predicted class
            predicted_class = np.argmax(probabilities)
            confidence = float(probabilities[predicted_class])
            
            # Get class information
            class_name = self.class_names[predicted_class]
            risk_info = self.risk_classification[predicted_class]
            
            # Create detailed results
            result = {
                'predicted_class': int(predicted_class),
                'class_name': class_name,
                'confidence': confidence,
                'risk_level': risk_info['risk'],
                'risk_color': risk_info['color'],
                'description': risk_info['description'],
                'all_probabilities': {
                    self.class_names[i]: float(prob) 
                    for i, prob in enumerate(probabilities)
                },
                'is_malignant': risk_info['risk'] == 'Malignant'
            }
            
            logger.info(f"Prediction made: {class_name} ({confidence:.2%} confidence)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def get_model_summary(self):
        """Get model architecture summary"""
        if self.model:
            return {
                'total_params': self.model.count_params(),
                'input_shape': self.input_shape,
                'num_classes': self.num_classes,
                'class_names': list(self.class_names.values()),
                'model_loaded': self.model_loaded
            }
        return None

# Utility function for easy model initialization
def create_model(model_path=None):
    """Create and return a SkinLesionClassifier instance"""
    return SkinLesionClassifier(model_path)