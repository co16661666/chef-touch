import cv2
import tools.markerDetector as markerDetector

# Configure webcam input
CAMERA_INDEX = 1  # 0 for default/built-in camera, 1+ for external cameras
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FPS = 30

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
        
        # Display results on frame
        if results:
            for marker_id, data in results.items():
                center = tuple(map(int, data["center"]))
                # Draw circle at marker center
                cv2.circle(frame, center, 10, (0, 255, 0), -1)
                # Draw marker ID
                cv2.putText(frame, f"ID: {marker_id}", 
                           (center[0] - 20, center[1] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
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
    print(f"Total frames processed: {frame_count}")

# Run the webcam marker detection
if __name__ == "__main__":
    detect_markers_from_webcam()