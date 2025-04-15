import os
import sys
import numpy as np
import cv2
from scipy.spatial.distance import cosine
import logging

# Suppress TensorFlow info/warnings/errors (optional if you're not using TensorFlow anymore)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Suppress specific warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow")

# Fix UnicodeEncodeError on Windows
sys.stdout.reconfigure(encoding='utf-8')

print("✔ TensorFlow logs suppressed. Only important results will be shown.")
UPLOAD_DIR = sys.argv[1] if len(sys.argv) > 1 else "./uploads"
print(f"📂 Using upload directory: {UPLOAD_DIR}")

def extract_features(img_path):
    """Extracts deep features using a simple method."""
    if not os.path.exists(img_path):
        print(f"❌ Error: File not found - {img_path}")
        return None

    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ Error: Could not read image - {img_path}")
        return None

    print(f"✔ Image successfully loaded: {img_path}")

    img = cv2.resize(img, (224, 224)) / 255.0  # Resize & normalize
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    # Simple feature extraction (using pixel values for comparison, for simplicity)
    features = img.flatten()  # Flatten the image into a 1D array (basic feature extraction)
    return features

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
    else:
        print(f"❌ Could not extract features from {img_file}")

# 🚨 Ensure valid feature vectors
if len(features) < 2:
    print("❌ Error: Could not extract features from both images.")
    sys.exit(0)

# ✅ Compute Cosine Similarity (Better than Euclidean)
similarity = 1 - cosine(features[0], features[1])

# 🚀 Use a Fixed Threshold for Stability
THRESHOLD = 0.95  # Adjust based on sensitivity

print("\n🔍 Image Comparison Result:")
if similarity is not None:
    print(f"📸 {filenames[0]} ↔ {filenames[1]} : Similarity = {similarity:.3f}")
    print(f"⚙️ Threshold: {THRESHOLD:.2f}")

    # 🚨 Detect changes based on threshold
    if similarity < THRESHOLD:
        print("⚠️ Significant change detected between the two images!")
        SIGNIFICANT_CHANGE_DETECTED = True
    else:
        print("✅ No significant differences detected.")
        SIGNIFICANT_CHANGE_DETECTED = False
else:
    print("❌ Error: Similarity calculation failed.")

print("🚀 Script execution complete. Exiting now...")
sys.exit(0)  # ✅ Ensures the script exits after running once
