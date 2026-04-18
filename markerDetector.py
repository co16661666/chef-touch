import cv2

def get_marker_dict(image_path):
    # 1. Load image
    image = cv2.imread(image_path)
    if image is None:
        print("Image not found.")
        return {}

    # 2. Configure Detector (matching your DICT_4X4_50)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # 3. Detect
    corners, ids, _ = detector.detectMarkers(image)

    # 4. Build Dictionary
    marker_data = {}

    if ids is not None:
        for marker_id, marker_corners in zip(ids.flatten(), corners):
            # marker_corners[0] is the 4x2 array of corners
            c = marker_corners[0]
            
            marker_data[int(marker_id)] = {
                "top_left":     c[0].tolist(),
                "top_right":    c[1].tolist(),
                "bottom_right": c[2].tolist(),
                "bottom_left":  c[3].tolist(),
                "center":       c.mean(axis=0).tolist() # Bonus: geometric center
            }

    return marker_data