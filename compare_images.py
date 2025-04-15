import os
import sys
import numpy as np
import cv2
from scipy.spatial.distance import cosine

# Function to extract features using ORB
def extract_orb_features(img_path):
    """Extract ORB keypoints and descriptors from the image."""
    if not os.path.exists(img_path):
        print(f"❌ Error: File not found - {img_path}")
        return None

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"❌ Error: Could not read image - {img_path}")
        return None

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Detect keypoints and descriptors
    keypoints, descriptors = orb.detectAndCompute(img, None)

    if descriptors is None:
        print(f"❌ Error: Could not extract descriptors - {img_path}")
        return None

    return descriptors

# Function to compute similarity using the number of matches
def compare_images(img1, img2):
    """Compare two images based on their ORB descriptors."""
    descriptors1 = extract_orb_features(img1)
    descriptors2 = extract_orb_features(img2)

    if descriptors1 is None or descriptors2 is None:
        return None

    # Use BFMatcher to find the best matches between descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches based on distance (lower is better)
    matches = sorted(matches, key=lambda x: x.distance)

    # Compute the ratio of good matches
    similarity = len(matches) / min(len(descriptors1), len(descriptors2))

    return similarity

# Directory containing the images to compare
UPLOAD_DIR = sys.argv[1] if len(sys.argv) > 1 else "./uploads"
print(f"📂 Using upload directory: {UPLOAD_DIR}")

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

# Extract features and compare
img1 = os.path.join(UPLOAD_DIR, image_files[0])
img2 = os.path.join(UPLOAD_DIR, image_files[1])

similarity = compare_images(img1, img2)

if similarity is None:
    print("❌ Error: Could not extract features from both images.")
    sys.exit(0)

# Define a similarity threshold
THRESHOLD = 0.6  # Adjust based on sensitivity

print("\n🔍 Image Comparison Result:")
print(f"📸 {image_files[0]} ↔ {image_files[1]} : Similarity = {similarity:.3f}")
print(f"⚙️ Threshold: {THRESHOLD:.2f}")

# 🚨 Detect changes based on threshold
if similarity < THRESHOLD:
    print("⚠️ Significant change detected between the two images!")
    SIGNIFICANT_CHANGE_DETECTED = True
else:
    print("✅ No significant differences detected.")
    SIGNIFICANT_CHANGE_DETECTED = False

sys.exit(0)  # ✅ Ensures the script exits after running once
