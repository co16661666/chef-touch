import numpy as np
import cv2 as cv
import glob

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points for 7x4 chessboard (7 columns, 4 rows)
# Points range from (0,0,0) to (6,3,0) = 28 total inner corners
objp = np.zeros((4*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:4].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# Webcam configuration
CAMERA_INDEX = 1
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FPS = 30

print("=== Camera Calibration - Live Webcam ===")
print("Press SPACEBAR to capture calibration image")
print("Press 'q' to quit and calculate calibration")
print()

# Initialize video capture
cap = cv.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print(f"Error: Cannot open camera at index {CAMERA_INDEX}")
    exit()

# Set video properties
cap.set(cv.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
cap.set(cv.CAP_PROP_FPS, FPS)

captured_frames = []
frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Failed to read frame")
        break
    
    frame_count += 1
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Display frame with info
    display_frame = frame.copy()
    cv.putText(display_frame, f"Captured: {len(captured_frames)} images", 
               (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv.putText(display_frame, "Press SPACE to capture, 'q' to quit", 
               (10, 70), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv.imshow("Camera Calibration - Press SPACE to capture", display_frame)
    
    key = cv.waitKey(1) & 0xFF
    
    if key == ord(' '):  # Spacebar
        captured_frames.append(gray)
        print(f"✓ Captured image {len(captured_frames)}")
    elif key == ord('q'):  # Quit
        print("\nCalculating calibration...")
        break

cap.release()
cv.destroyAllWindows()

print(f"\nTotal images captured: {len(captured_frames)}")
print("Looking for 8x5 chessboard pattern (8 columns x 5 rows = 40 inner corners)...")
print("\nNOTE: If no chessboards are found, common reasons are:")
print("  1. Chessboard not fully visible in frame")
print("  2. Wrong pattern size")
print("  3. Poor lighting or contrast")
print("  4. Image blur or motion")
print()

pattern_sizes = [(8,5)]

for idx, gray in enumerate(captured_frames):
    found = False
    
    for pattern_size in pattern_sizes:
        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, pattern_size, None)
        
        if ret == True:
            # Use the correct objp for this pattern size
            cols, rows = pattern_size
            temp_objp = np.zeros((rows*cols, 3), np.float32)
            temp_objp[:,:2] = np.mgrid[0:cols, 0:rows].T.reshape(-1,2)
            
            objpoints.append(temp_objp)
            corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
            
            print(f"✓ Image {idx + 1}: Found {cols}x{rows} chessboard")
            found = True
            break
    
    if not found:
        print(f"✗ Image {idx + 1}: Chessboard not found")

print(f"\nTotal images with chessboard detected: {len(objpoints)}")

# Perform camera calibration
if len(objpoints) > 0:
    print(f"\nCalibrating camera with {len(objpoints)} images...")
    
    # Get image size
    img_size = gray.shape[::-1] # type: ignore
    
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, img_size, None, None) # type: ignore
    
    print("\n=== Calibration Results ===")
    print(f"Reprojection error: {ret:.4f} pixels")
    print(f"\nCamera Matrix (mtx):")
    print(mtx)
    print(f"\nDistortion Coefficients (dist):")
    print(dist)
    
    # Save calibration results
    np.savez('calibration_data.npz', 
             camera_matrix=mtx, 
             dist_coeffs=dist,
             rvecs=rvecs,
             tvecs=tvecs)
    print("\n✓ Calibration data saved to 'calibration_data.npz'")
else:
    print("\n✗ Error: No chessboard patterns found in any images!")
    print("   Cannot perform calibration without detected patterns.")