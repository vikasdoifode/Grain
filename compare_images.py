import os
import sys
import numpy as np
import cv2
import tensorflow as tf
from scipy.spatial.distance import cosine
import serial  # For Serial Communication
import time


# 🔇 Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

# ✅ Fix Unicode errors in Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# ✅ Set upload directory
UPLOAD_DIR = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/DELL/OneDrive/Desktop/Grain/uploads"
print(f"📂 Using upload directory: {UPLOAD_DIR}")

# ✅ Load ResNet-50 model (Pretrained on ImageNet)
model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    weights="imagenet",
    include_top=False,
    pooling="avg"
)


def extract_features(img_path):
    """Extracts deep features using ResNet-50."""
    if not os.path.exists(img_path):
        print(f"❌ Error: File not found - {img_path}")
        return None

    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ Error: Could not read image - {img_path}")
        return None

    img = cv2.resize(img, (224, 224)) / 255.0  # Resize & normalize
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    # Extract deep features
    features = model.predict(img, verbose=0)
    return features.flatten()  # Convert to 1D vector

# ✅ Get the latest 2 images (For direct comparison)
image_files = sorted(
    [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))],
    key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)),
    reverse=True
)[:2]

# 🚨 Ensure we have at least 2 images for comparison
if len(image_files) < 2:
    print("📸 Not enough images for comparison.")
    sys.exit(0)

# ✅ Extract features
features = []
filenames = []

for img_file in image_files:
    img_path = os.path.join(UPLOAD_DIR, img_file)
    feature_vector = extract_features(img_path)
    if feature_vector is not None:
        features.append(feature_vector)
        filenames.append(img_file)

# 🚨 Ensure valid feature vectors
if len(features) < 2:
    print("❌ Error: Could not extract features from both images.")
    sys.exit(0)

# ✅ Compute Cosine Similarity (Better than Euclidean)
similarity = 1 - cosine(features[0], features[1])

# 🚀 Use a Fixed Threshold for Stability
THRESHOLD = 0.95  # Adjust based on sensitivity

print("\n🔍 Image Comparison Result:")
print(f"📸 {filenames[0]} ↔ {filenames[1]} : Similarity = {similarity:.3f}")
print(f"⚙️ Threshold: {THRESHOLD:.2f}")

# 🚨 Detect changes based on threshold
if similarity < THRESHOLD:
    print("⚠️ Significant change detected between the two images!")
    SIGNIFICANT_CHANGE_DETECTED = True
else:
    print("✅ No significant differences detected.")
    SIGNIFICANT_CHANGE_DETECTED = False

print("🚀 Script execution complete. Exiting now...")

# Open Serial Port (Change COM3 to your actual NodeMCU COM port)
ser = serial.Serial('COM4', 115200, timeout=1)
time.sleep(2)  # Wait for connection

# 🚨 Change this variable based on your detection logic
  # Replace this with your actual detection result

if SIGNIFICANT_CHANGE_DETECTED:
    print("⚠️ Significant change detected! Sending LED_ON signal to NodeMCU...")
    ser.write(b'LED_ON\n')  # Send signal to NodeMCU
else:
    print("✅ No significant change detected. Sending LED_OFF signal to NodeMCU...")
    ser.write(b'LED_OFF\n')  # Send signal to NodeMCU

ser.close()  # Close Serial Connection


sys.exit(0)  # ✅ Ensures the script exits after running once
