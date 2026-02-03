import os
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


class DiagnosisModel:
    """Machine Learning model for symptom-based diagnosis prediction with enhanced training"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), 
            'models', 
            'diagnosis_model.joblib'
        )
        self.condition_encoder = None
        self.specialization_encoder = None
        self.symptom_list = None
        self.model = None
        self.specialization_model = None
        self.cv_scores = {}
        self.load_model()

    def load_model(self):
        """Load the trained model and encoders from disk"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data.get('model')
                self.specialization_model = model_data.get('specialization_model')
                self.condition_encoder = model_data.get('condition_encoder')
                self.specialization_encoder = model_data.get('specialization_encoder')
                self.symptom_list = model_data.get('symptom_list')
                self.cv_scores = model_data.get('cv_scores', {})
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        return False

    def save_model(self):
        """Save the trained model and encoders to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        model_data = {
            'model': self.model,
            'specialization_model': self.specialization_model,
            'condition_encoder': self.condition_encoder,
            'specialization_encoder': self.specialization_encoder,
            'symptom_list': self.symptom_list,
            'cv_scores': self.cv_scores
        }
        joblib.dump(model_data, self.model_path)

    def _hyperparameter_tuning(self, X, y):
        """Perform grid search for hyperparameter optimization"""
        print("🔍 Performing hyperparameter tuning...")
        
        # Use 2-fold CV for small datasets, 3-fold for larger ones
        n_splits = 2 if len(X) < 50 else 3
        
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [8, 10],
            'min_samples_split': [2, 5],
        }
        
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=42, n_jobs=-1),
            param_grid,
            cv=n_splits,
            scoring='accuracy',
            n_jobs=-1
        )
        
        grid_search.fit(X, y)
        print(f"✓ Best parameters: {grid_search.best_params_}")
        print(f"✓ Best CV Score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_

    def _cross_validation(self, model, X, y, task_name):
        """Perform stratified k-fold cross validation"""
        # Count samples per class to determine max k
        unique, counts = np.unique(y, return_counts=True)
        min_samples = np.min(counts)
        n_splits = min(2, min_samples)  # Use 2-fold CV for small datasets
        
        if n_splits < 2:
            print(f"📊 Skipping cross-validation for {task_name} (insufficient samples per class)")
            return np.array([model.score(X, y)])
        
        print(f"📊 Running {n_splits}-fold cross-validation for {task_name}...")
        
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy', n_jobs=-1)
        
        print(f"   CV Scores: {[f'{score:.4f}' for score in cv_scores]}")
        print(f"   Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return cv_scores

    def train(self, dataset_path, use_hyperparameter_tuning=True, use_cross_validation=True):
        """
        Train the model using dataset with optional hyperparameter tuning and cross-validation
        
        Dataset format (CSV):
        - symptoms: comma-separated symptom names
        - condition: medical condition name
        - specialization: medical specialization name
        """
        try:
            df = pd.read_csv(dataset_path)
            
            # Initialize encoders
            self.condition_encoder = LabelEncoder()
            self.specialization_encoder = LabelEncoder()
            
            # Fit encoders
            df['condition_encoded'] = self.condition_encoder.fit_transform(df['condition'])
            df['specialization_encoded'] = self.specialization_encoder.fit_transform(df['specialization'])
            
            # Extract unique symptoms
            all_symptoms = set()
            for symptoms_str in df['symptoms']:
                all_symptoms.update([s.strip() for s in symptoms_str.split(',')])
            self.symptom_list = sorted(list(all_symptoms))
            
            # Create feature vectors
            X = []
            for symptoms_str in df['symptoms']:
                symptom_vector = [0] * len(self.symptom_list)
                present_symptoms = [s.strip() for s in symptoms_str.split(',')]
                for symptom in present_symptoms:
                    if symptom in self.symptom_list:
                        symptom_vector[self.symptom_list.index(symptom)] = 1
                X.append(symptom_vector)
            
            X = np.array(X)
            y_condition = df['condition_encoded'].values
            y_specialization = df['specialization_encoded'].values
            
            # Train condition model with optional hyperparameter tuning
            print("🤖 Training condition prediction model...")
            if use_hyperparameter_tuning and len(X) > 20:
                self.model = self._hyperparameter_tuning(X, y_condition)
            else:
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                self.model.fit(X, y_condition)
            
            # Perform cross-validation if requested
            if use_cross_validation:
                cv_condition = self._cross_validation(self.model, X, y_condition, "Condition Prediction")
                self.cv_scores['condition'] = {
                    'mean': float(cv_condition.mean()),
                    'std': float(cv_condition.std())
                }
            
            # Train specialization model
            print("🤖 Training specialization prediction model...")
            self.specialization_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.specialization_model.fit(X, y_specialization)
            
            if use_cross_validation:
                cv_specialization = self._cross_validation(self.specialization_model, X, y_specialization, "Specialization Prediction")
                self.cv_scores['specialization'] = {
                    'mean': float(cv_specialization.mean()),
                    'std': float(cv_specialization.std())
                }
            
            self.save_model()
            print("✓ Model training completed and saved!")
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False

    def predict_condition(self, symptom_names):
        """
        Predict medical condition and specialization from symptoms
        
        Args:
            symptom_names: list of symptom names (present symptoms)
            
        Returns:
            (predicted_condition, predicted_specialization, confidence_score)
        """
        if not self.model or not self.specialization_model or not self.symptom_list:
            return None, None, 0.0
        
        try:
            # Create feature vector
            symptom_vector = np.zeros(len(self.symptom_list))
            for symptom in symptom_names:
                if symptom in self.symptom_list:
                    symptom_vector[self.symptom_list.index(symptom)] = 1
            
            # Predict condition
            symptom_vector_2d = symptom_vector.reshape(1, -1)
            condition_pred = self.model.predict(symptom_vector_2d)[0]
            specialization_pred = self.specialization_model.predict(symptom_vector_2d)[0]
            
            # Get probabilities for confidence
            condition_proba = self.model.predict_proba(symptom_vector_2d)
            confidence = np.max(condition_proba[0])
            
            # Decode predictions
            predicted_condition = self.condition_encoder.inverse_transform([condition_pred])[0]
            predicted_specialization = self.specialization_encoder.inverse_transform([specialization_pred])[0]
            
            return predicted_condition, predicted_specialization, float(confidence)
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None, None, 0.0

    def get_model_info(self):
        """Get model information and cross-validation scores"""
        info = {
            'symptoms_count': len(self.symptom_list) if self.symptom_list else 0,
            'conditions_count': len(self.condition_encoder.classes_) if self.condition_encoder else 0,
            'specializations_count': len(self.specialization_encoder.classes_) if self.specialization_encoder else 0,
            'cv_scores': self.cv_scores
        }
        return info


# Global instance
_diagnosis_model = None


def get_diagnosis_model():
    """Get or create the global diagnosis model instance"""
    global _diagnosis_model
    if _diagnosis_model is None:
        _diagnosis_model = DiagnosisModel()
    return _diagnosis_model
