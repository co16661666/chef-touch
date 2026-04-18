import cv2
import numpy as np


# points matrix: [[100, 50], [600, 60], [90, 500], [610, 510]]
# camera_matrix: np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
# dist_coeffs: np.array([k1, k2, p1, p2])
def calculate_homography_from_markers(marker_corners, dest_points, camera_matrix=None, dist_coeffs=None):
    # Convert to numpy arrays
    src_points = np.array(marker_corners, dtype=np.float32)
    dst_points = np.array(dest_points, dtype=np.float32)
    
    # Validate input shapes
    if src_points.shape != (4, 2):
        raise ValueError(f"marker_corners must have shape (4, 2), got {src_points.shape}")
    if dst_points.shape != (4, 2):
        raise ValueError(f"dest_points must have shape (4, 2), got {dst_points.shape}")
    
    # Undistort source points if camera parameters are provided
    if camera_matrix is not None and dist_coeffs is not None:
        camera_matrix = np.array(camera_matrix, dtype=np.float32)
        dist_coeffs = np.array(dist_coeffs, dtype=np.float32)
        
        # Reshape for undistortPoints (needs shape (n, 1, 2))
        src_points_reshaped = src_points.reshape(-1, 1, 2)
        
        # Undistort the points
        src_points_undist = cv2.undistortPoints(src_points_reshaped, camera_matrix, dist_coeffs)
        src_points = src_points_undist.reshape(-1, 2)
    
    # Calculate homography using RANSAC for robustness
    homography_matrix, status = cv2.findHomography(src_points, dst_points, cv2.RANSAC, ransacReprojThreshold=5.0)
    
    if homography_matrix is None:
        print("Warning: Homography calculation failed. Trying without RANSAC...")
        homography_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        status = np.ones((4, 1), dtype=np.uint8)
    
    return homography_matrix, status


def transform_points_with_homography(points, homography_matrix):
    if homography_matrix is None:
        print("Error: Homography matrix is None")
        return None
    
    points = np.array(points, dtype=np.float32)
    
    # Reshape for perspectiveTransform (needs shape (n, 1, 2))
    points_reshaped = points.reshape(-1, 1, 2)
    
    # Transform points using homography
    transformed = cv2.perspectiveTransform(points_reshaped, homography_matrix)
    
    return transformed.reshape(-1, 2)


def validate_homography(homography_matrix, src_points, dst_points, threshold=5.0):
    src_points = np.array(src_points, dtype=np.float32).reshape(-1, 1, 2)
    dst_expected = np.array(dst_points, dtype=np.float32)
    
    # Project source points using homography
    dst_projected = cv2.perspectiveTransform(src_points, homography_matrix).reshape(-1, 2)
    
    # Calculate reprojection error
    errors = np.linalg.norm(dst_projected - dst_expected, axis=1)
    mean_error = np.mean(errors)
    max_error = np.max(errors)
    
    is_valid = mean_error < threshold
    
    print(f"Homography validation - Mean Error: {mean_error:.2f}px, Max Error: {max_error:.2f}px")
    
    return is_valid, mean_error
