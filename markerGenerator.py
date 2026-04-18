import cv2
import numpy as np

# 1. Setup Dictionary
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# 2. Define Parameters
markerIds = list(range(0, 10)) # 10 markers
markerSize = 92                # pixels
margin = 45                    # space between markers and edges

# 3. Define Grid Layout (2 rows x 5 columns = 10 markers)
rows = 2
cols = 5

# 4. Calculate Grid Dimensions
gridHeight = rows * (markerSize + margin) + margin
gridWidth = cols * (markerSize + margin) + margin

# 5. Create Blank Canvas (White)
grid = np.full((gridHeight, gridWidth), 255, dtype=np.uint8)

# 6. Place Markers
for i, marker_id in enumerate(markerIds):
    row_idx = i // cols  # Determines which row (0 or 1)
    col_idx = i % cols   # Determines which column (0 to 4)
    
    startY = row_idx * (markerSize + margin) + margin
    startX = col_idx * (markerSize + margin) + margin
    
    # Generate the marker
    marker_img = cv2.aruco.generateImageMarker(arucoDict, marker_id, markerSize)
    
    # Place in grid
    grid[startY:startY + markerSize, startX:startX + markerSize] = marker_img

# 7. Save Result
cv2.imwrite("marker_grid_10.png", grid, [cv2.IMWRITE_PNG_COMPRESSION, 0])
print(f"Generated a {rows}x{cols} grid with {len(markerIds)} markers.")