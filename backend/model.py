import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_PATH = os.path.join(os.path.dirname(__file__), "helmet_model.joblib")

def generate_synthetic_data(num_samples=1200):
    """
    Generates synthetic helmet sensor dataset.
    Features:
      - speed (km/h)
      - vibration (vibration amplitude, 0 to 20)
      - alcohol_level (BAC index, 0.0 to 1.0)
      - drowsy_score (0.0 to 1.0, drowsiness index)
      - accel_x, accel_y, accel_z (in Gs, normal Z is ~1.0)
      - gyro_x, gyro_y, gyro_z (in deg/s, normal is ~0)
    
    Labels:
      - 0: Safe
      - 1: At-Risk
      - 2: Danger
    """
    np.random.seed(42)
    
    # Generate random features
    speed = np.random.uniform(0, 110, num_samples)
    vibration = np.random.uniform(0.2, 18.0, num_samples)
    alcohol_level = np.random.uniform(0.0, 0.8, num_samples)
    drowsy_score = np.random.uniform(0.0, 1.0, num_samples)
    accel_x = np.random.uniform(-2.0, 2.0, num_samples)
    accel_y = np.random.uniform(-2.0, 2.0, num_samples)
    accel_z = np.random.uniform(0.5, 1.5, num_samples) # normal gravity is ~1.0 G
    gyro_x = np.random.uniform(-45.0, 45.0, num_samples)
    gyro_y = np.random.uniform(-45.0, 45.0, num_samples)
    gyro_z = np.random.uniform(-45.0, 45.0, num_samples)
    
    data = pd.DataFrame({
        "speed": speed,
        "vibration": vibration,
        "alcohol_level": alcohol_level,
        "drowsy_score": drowsy_score,
        "accel_x": accel_x,
        "accel_y": accel_y,
        "accel_z": accel_z,
        "gyro_x": gyro_x,
        "gyro_y": gyro_y,
        "gyro_z": gyro_z
    })
    
    # Initialize labels
    labels = []
    
    for i in range(num_samples):
        s = data.iloc[i]["speed"]
        v = data.iloc[i]["vibration"]
        alc = data.iloc[i]["alcohol_level"]
        drw = data.iloc[i]["drowsy_score"]
        ax = data.iloc[i]["accel_x"]
        ay = data.iloc[i]["accel_y"]
        az = data.iloc[i]["accel_z"]
        gx = data.iloc[i]["gyro_x"]
        gy = data.iloc[i]["gyro_y"]
        
        # Danger conditions (Crash / Heavy Drunk / High speed + high drowsy)
        if v > 12.0 or abs(ax) > 3.0 or abs(ay) > 3.0 or (s > 40 and v > 8.0):
            # Sudden high impact (crash / fall)
            labels.append(2) # Danger
        elif alc >= 0.35:
            # Heavily drunk
            labels.append(2) # Danger
        elif drw >= 0.75 and s > 50:
            # Sleeping while speeding
            labels.append(2) # Danger
            
        # At-Risk conditions
        elif s > 80:
            # Overspeeding
            labels.append(1) # At-Risk
        elif 0.15 <= alc < 0.35:
            # Moderate alcohol detected
            labels.append(1) # At-Risk
        elif 0.5 <= drw < 0.75:
            # Moderate drowsiness
            labels.append(1) # At-Risk
        elif abs(gx) > 35.0 or abs(gy) > 35.0:
            # Unstable driving (high tilt / swerving)
            labels.append(1) # At-Risk
            
        # Safe conditions
        else:
            labels.append(0) # Safe
            
    data["label"] = labels
    return data

def train_model():
    """Trains and saves the Random Forest classifier model."""
    print("Generating synthetic helmet sensor data...")
    df = generate_synthetic_data(1500)
    
    X = df.drop(columns=["label"])
    y = df["label"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=80, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    
    print(f"Model Training Complete.")
    print(f"Training Accuracy: {train_acc:.4f}")
    print(f"Testing Accuracy: {test_acc:.4f}")
    
    # Save the model
    joblib.dump(model, MODEL_PATH)
    print(f"Saved trained model to {MODEL_PATH}")
    return model

def load_or_train_model():
    """Loads the model if it exists, otherwise trains it."""
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Error loading model: {e}. Re-training...")
            return train_model()
    else:
        return train_model()

# Load model globally
model = load_or_train_model()

def predict_status(sensor_data: dict) -> dict:
    """
    Takes sensor readings dictionary and returns prediction.
    Expected keys: speed, vibration, alcohol_level, drowsy_score,
                   accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
    """
    # Order of features must match the training set
    feature_names = [
        "speed", "vibration", "alcohol_level", "drowsy_score",
        "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"
    ]
    
    # Construct feature array
    try:
        features = [float(sensor_data.get(name, 0.0)) for name in feature_names]
        features_arr = np.array([features])
        
        prediction = model.predict(features_arr)[0]
        probabilities = model.predict_proba(features_arr)[0]
        
        status_map = {0: "Safe", 1: "At-Risk", 2: "Danger"}
        
        return {
            "status": status_map[prediction],
            "class_probabilities": {
                "Safe": float(probabilities[0]),
                "At-Risk": float(probabilities[1]),
                "Danger": float(probabilities[2])
            }
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {
            "status": "Safe",
            "error": str(e),
            "class_probabilities": {"Safe": 1.0, "At-Risk": 0.0, "Danger": 0.0}
        }

if __name__ == "__main__":
    # If run directly, force re-train
    train_model()
