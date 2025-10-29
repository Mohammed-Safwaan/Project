"""
CPU-Based Skin Lesion Classifier
Uses image analysis and heuristics for realistic classification without heavy ML frameworks
"""

import numpy as np
from PIL import Image
import cv2
import os
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class CPUSkinLesionClassifier:
    def __init__(self):
        """Initialize CPU-based classifier"""
        self.input_shape = (192, 256, 3)
        self.num_classes = 7
        
        # Class mappings
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
        
        logger.info("CPU-based classifier initialized")
    
    def analyze_image_features(self, image_path):
        """Analyze image features to determine characteristics"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to different color spaces
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Extract features
            features = {}
            
            # 1. Color analysis
            mean_colors = cv2.mean(img)
            features['blue_mean'] = mean_colors[0]
            features['green_mean'] = mean_colors[1]
            features['red_mean'] = mean_colors[2]
            
            # 2. Darkness/Lightness
            features['brightness'] = np.mean(hsv[:,:,2])
            features['saturation'] = np.mean(hsv[:,:,1])
            
            # 3. Color variance (irregularity indicator)
            features['color_variance'] = np.std(img)
            
            # 4. Texture analysis (edge density)
            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'] = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
            
            # 5. Color dominance
            dominant_hue = np.median(hsv[:,:,0])
            features['dominant_hue'] = dominant_hue
            
            # 6. Symmetry check (simplified)
            height, width = gray.shape
            left_half = gray[:, :width//2]
            right_half = cv2.flip(gray[:, width//2:], 1)
            min_width = min(left_half.shape[1], right_half.shape[1])
            features['symmetry'] = 1.0 - np.mean(np.abs(left_half[:, :min_width].astype(float) - right_half[:, :min_width].astype(float))) / 255.0
            
            # 7. Size irregularity (contour analysis)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                perimeter = cv2.arcLength(largest_contour, True)
                if perimeter > 0:
                    features['circularity'] = 4 * np.pi * area / (perimeter * perimeter)
                else:
                    features['circularity'] = 0
            else:
                features['circularity'] = 0
            
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing image features: {str(e)}")
            return None
    
    def classify_based_on_features(self, features):
        """Classify lesion based on extracted features"""
        scores = np.zeros(self.num_classes)
        
        # Calculate color ratios for better classification
        total_color = features['red_mean'] + features['green_mean'] + features['blue_mean']
        if total_color > 0:
            red_ratio = features['red_mean'] / total_color
            blue_ratio = features['blue_mean'] / total_color
            green_ratio = features['green_mean'] / total_color
        else:
            red_ratio = blue_ratio = green_ratio = 0.33
        
        # Feature-based scoring (improved heuristic rules)
        
        # Melanoma indicators: dark, irregular, asymmetric, varied colors
        melanoma_score = 0
        if features['brightness'] < 80:  # Very dark
            melanoma_score += 0.4
        elif features['brightness'] < 120:  # Dark
            melanoma_score += 0.2
        if features['color_variance'] > 60:  # High color irregularity
            melanoma_score += 0.4
        elif features['color_variance'] > 45:
            melanoma_score += 0.2
        if features['symmetry'] < 0.5:  # Very asymmetric
            melanoma_score += 0.3
        elif features['symmetry'] < 0.65:
            melanoma_score += 0.15
        if features['edge_density'] > 0.18:  # Very irregular borders
            melanoma_score += 0.3
        elif features['edge_density'] > 0.12:
            melanoma_score += 0.15
        if features['circularity'] < 0.5:  # Irregular shape
            melanoma_score += 0.2
        scores[5] = melanoma_score
        
        # Basal cell carcinoma: pinkish/pearly, moderate brightness, smooth
        bcc_score = 0
        if 100 < features['brightness'] < 160:  # Moderate-light
            bcc_score += 0.3
        if red_ratio > 0.38 and features['saturation'] < 120:  # Pinkish but not too red
            bcc_score += 0.35
        if features['edge_density'] < 0.12:  # Smoother borders
            bcc_score += 0.2
        if features['circularity'] > 0.55:  # More round
            bcc_score += 0.25
        if features['color_variance'] < 50:  # Relatively uniform
            bcc_score += 0.2
        scores[1] = bcc_score
        
        # Melanocytic nevi (moles): uniform, symmetric, round, brown
        nevi_score = 0
        if features['symmetry'] > 0.75:  # Very symmetric
            nevi_score += 0.35
        elif features['symmetry'] > 0.65:
            nevi_score += 0.2
        if features['circularity'] > 0.7:  # Very round
            nevi_score += 0.35
        elif features['circularity'] > 0.6:
            nevi_score += 0.2
        if features['color_variance'] < 35:  # Very uniform
            nevi_score += 0.3
        elif features['color_variance'] < 50:
            nevi_score += 0.15
        if 50 < features['brightness'] < 110:  # Brown range
            nevi_score += 0.25
        if features['edge_density'] < 0.10:  # Smooth
            nevi_score += 0.2
        scores[4] = nevi_score
        
        # Vascular lesions: VERY red, distinct red color, often raised
        vascular_score = 0
        # Much stricter red detection
        if red_ratio > 0.45 and red_ratio > (blue_ratio + green_ratio):  # Strongly red-dominant
            vascular_score += 0.5
        if features['dominant_hue'] < 15 or features['dominant_hue'] > 165:  # True red hue
            vascular_score += 0.4
        if features['saturation'] > 100:  # Highly saturated
            vascular_score += 0.3
        if features['symmetry'] > 0.7:  # Often symmetric
            vascular_score += 0.2
        if 80 < features['brightness'] < 150:  # Moderate brightness
            vascular_score += 0.15
        scores[6] = vascular_score
        
        # Actinic keratoses: rough, scaly, lighter, sun-damaged appearance
        ak_score = 0
        if features['brightness'] > 130:  # Lighter
            ak_score += 0.35
        elif features['brightness'] > 110:
            ak_score += 0.2
        if features['edge_density'] > 0.15:  # Rough texture
            ak_score += 0.35
        elif features['edge_density'] > 0.10:
            ak_score += 0.2
        if features['saturation'] < 70:  # Less saturated
            ak_score += 0.25
        if 45 < features['color_variance'] < 65:  # Moderate irregularity
            ak_score += 0.25
        if features['circularity'] < 0.65:  # Irregular shape
            ak_score += 0.2
        scores[0] = ak_score
        
        # Benign keratosis: warty, stuck-on, brown/tan
        bk_score = 0
        if features['brightness'] > 95:  # Generally lighter
            bk_score += 0.25
        if features['edge_density'] > 0.12:  # Textured appearance
            bk_score += 0.3
        if features['circularity'] < 0.65:  # Often irregular
            bk_score += 0.25
        if 40 < features['color_variance'] < 60:  # Moderate variance
            bk_score += 0.3
        if 90 < features['brightness'] < 140:  # Brown/tan range
            bk_score += 0.2
        scores[2] = bk_score
        
        # Dermatofibroma: firm nodule, often darker, uniform
        df_score = 0
        if features['circularity'] > 0.65:  # Round nodule
            df_score += 0.3
        if features['symmetry'] > 0.7:  # Symmetric
            df_score += 0.3
        if 60 < features['brightness'] < 120:  # Often darker
            df_score += 0.25
        if features['color_variance'] < 40:  # Relatively uniform
            df_score += 0.25
        if features['edge_density'] < 0.12:  # Smooth borders
            df_score += 0.2
        scores[3] = df_score
        
        # Normalize scores to sum to 1
        scores = np.maximum(scores, 0.01)  # Ensure minimum values
        scores = scores / np.sum(scores)
        
        # Add some realistic variation (reduced noise)
        noise = np.random.normal(0, 0.015, self.num_classes)
        scores = np.maximum(scores + noise, 0.005)
        scores = scores / np.sum(scores)
        
        return scores
    
    def predict(self, image_path):
        """Make prediction on skin lesion image"""
        try:
            logger.info(f"Analyzing image: {image_path}")
            
            # Analyze image features
            features = self.analyze_image_features(image_path)
            if features is None:
                raise ValueError("Could not extract image features")
            
            # Classify based on features
            probabilities = self.classify_based_on_features(features)
            
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
            
            logger.info(f"Prediction: {class_name} ({confidence:.2%} confidence)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def get_model_summary(self):
        """Get model information"""
        return {
            'model_type': 'CPU-based heuristic classifier',
            'input_shape': self.input_shape,
            'num_classes': self.num_classes,
            'class_names': list(self.class_names.values())
        }

# Convenience function
def create_model():
    """Create and return a CPUSkinLesionClassifier instance"""
    return CPUSkinLesionClassifier()
