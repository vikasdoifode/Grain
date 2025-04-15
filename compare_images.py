import os
import sys
import cv2
import numpy as np

def compute_similarity(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        print(f"❌ Failed to load one of the images.")
        return None

    orb = cv2.ORB_create()

    # Find keypoints and descriptors
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        print("❌ Could not extract descriptors.")
        return None

    # Match features using Hamming distance
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    # Sort matches by distance
    matches = sorted(matches, key=lambda x: x.distance)

    # Use a similarity score: number of good matches over total keypoints
    good_match_count = len(matches)
    max_keypoints = max(len(kp1), len(kp2))
    similarity = good_match_count / max_keypoints if max_keypoints != 0 else 0

    return similarity

# Entry Point
UPLOAD_DIR = sys.argv[1] if len(sys.argv) > 1 else "./uploads"
print(f"📂 Using upload directory: {UPLOAD_DIR}")

# Get the latest 2 images
image_files = sorted(
    [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))],
    key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)),
    reverse=True
)[:2]

if len(image_files) < 2:
    print("📸 Not enough images for comparison.")
    sys.exit(0)

# Compute similarity
img1_path = os.path.join(UPLOAD_DIR, image_files[0])
img2_path = os.path.join(UPLOAD_DIR, image_files[1])

similarity = compute_similarity(img1_path, img2_path)
THRESHOLD = 0.3  # Lower threshold since ORB gives smaller values

print("\n🔍 Image Comparison Result:")
print(f"📸 {image_files[0]} ↔ {image_files[1]} : Similarity = {similarity:.3f}")
print(f"⚙️ Threshold: {THRESHOLD:.2f}")

if similarity < THRESHOLD:
    print("⚠️ Significant change detected between the two images!")
else:
    print("✅ No significant differences detected.")

print("🚀 Script execution complete. Exiting now...")
sys.exit(0)
