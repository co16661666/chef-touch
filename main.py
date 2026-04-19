import cv2
import tools.markerDetector as markerDetector
import storylines.story0 as story0
import tools.pointCorrection as pointCorrection

from enum import Enum

import serial
import serial.tools.list_ports
from tools.asyncSerial import AsyncSerialReader
print("Serial ports available:", serial.tools.list_ports.comports())
reader = AsyncSerialReader('COM15', 115200)

class TagName(Enum):
    MAT_TL = 1
    MAT_TR = 2
    MAT_BR = 3
    MAT_BL = 4

    MIX_PLATE = 5
    PLATE_A = 6
    PLATE_B = 7

# Configure webcam input
CAMERA_INDEX = 1  # 0 for default/built-in camera, 1+ for external cameras
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FPS = 30

# Marker board dimensions (relative to marker 0) - in mm
# Marker 0 is at origin, specify other markers' positions relative to it
MARKER_LAYOUT = {
    0: [0, 0],
    1: [60.1 * 10, 0],
    2: [60.1 * 10, 41.1 * 10],
    3: [0, 40.5 * 10],
}

# Anchor marker IDs (calibration markers)
ANCHOR_MARKERS = [0, 1, 2, 3]

CAMERA_MATRIX = [[944.42008778,   0.,         635.58550724],
                [  0.,         944.2831632,  359.07690285],
                [  0.,           0.,           1.        ]]
DIST_COEFFS = [[ 3.03516621e-01, -2.05751194e+00,  1.45973957e-03,  6.58486098e-04, 4.01649152e+00]]

def detect_markers_from_webcam():
    """
    Capture video from external webcam and detect markers in real-time.
    Press 'q' to quit.
    """
    # Initialize video capture
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print(f"Error: Cannot open camera at index {CAMERA_INDEX}")
        return
    
    # Set video properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    
    print(f"Camera opened successfully at index {CAMERA_INDEX}")
    print("Press 'q' to quit")
    
    frame_count = 0
    
    game_story = None
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to read frame")
            break
        
        frame_count += 1
        
        # Convert frame to temporary image file for processing
        temp_image_path = "temp_frame.png"
        cv2.imwrite(temp_image_path, frame)
        
        # Detect markers in the frame
        results = markerDetector.get_marker_dict(temp_image_path)
        
        # Apply point correction if calibration markers are present
        if results and all(marker_id in results for marker_id in [0, 1, 2, 3]):
            # Extract top-left corners of calibration markers
            calibration_corners = [
                results[0]["top_left"],
                results[1]["top_left"],
                results[2]["top_left"],
                results[3]["top_left"]
            ]
            
            # Define destination points relative to marker 0 (at origin)
            dest_points = [
                MARKER_LAYOUT[0],
                MARKER_LAYOUT[1],
                MARKER_LAYOUT[2],
                MARKER_LAYOUT[3]
            ]
            
            # Calculate homography
            H, status = pointCorrection.calculate_homography_from_markers(
                calibration_corners, 
                dest_points,
                camera_matrix=CAMERA_MATRIX,
                dist_coeffs=DIST_COEFFS
            )
            
            if H is not None:
                # Transform all detected points using homography
                # Extract points maintaining marker ID association
                corrected_results = {}
                
                for marker_id, data in results.items():
                    top_left = data["top_left"]
                    
                    # Transform single point using homography
                    point_array = [[top_left]]
                    transformed = pointCorrection.transform_points_with_homography(
                        point_array, H
                    )
                    
                    if transformed is not None:
                        corrected_data = data.copy()
                        corrected_data["top_left_corrected"] = transformed[0].tolist()
                        corrected_results[marker_id] = corrected_data
                    else:
                        corrected_results[marker_id] = data
                
                results = corrected_results
        
        # Initialize story on first frame with game object markers detected
        if game_story is None and results and all(marker_id in results for marker_id in [4, 5, 6]):
            game_story = story0.Story0(results)
            print("Game initialized with detected marker positions")
        
        # Update story with current marker positions
        if game_story is not None and results:
            game_story.update(results)
            actions = reader.get_latest()
            # TODO: Process game logic (cutting, mixing, serving)
            # game_story.processCutting()
            # game_story.processMixing()
            # if game_story.checkComplete():
            #     print("Story Complete!")
        
        # Display results on frame
        if results:
            for marker_id, data in results.items():
                # Mark top-left corner for all markers
                top_left = tuple(map(int, data["top_left"]))
                cv2.circle(frame, top_left, 8, (0, 255, 0), -1)
                # Draw marker ID
                cv2.putText(frame, f"ID: {marker_id}", 
                           (top_left[0] + 10, top_left[1] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Display corrected position in mm for non-anchor markers
                if "top_left_corrected" in data and marker_id not in ANCHOR_MARKERS:
                    corrected_tl = data["top_left_corrected"]
                    # Corrected position is already in mm (from homography using MARKER_LAYOUT values)
                    position_mm_x = corrected_tl[0]
                    position_mm_y = corrected_tl[1]
                    
                    cv2.putText(frame, f"({position_mm_x:.1f}, {position_mm_y:.1f})mm", 
                               (top_left[0] + 10, top_left[1] + 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            
            print(f"Frame {frame_count}: Detected {len(results)} markers")
        
        # Display frame with detections
        cv2.imshow("Marker Detection - External Webcam", frame)
        
        # Check for quit command
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    reader.stop()
    print(f"Total frames processed: {frame_count}")

# Run the webcam marker detection
if __name__ == "__main__":
    detect_markers_from_webcam()