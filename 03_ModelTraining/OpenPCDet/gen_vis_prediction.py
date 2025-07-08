import open3d as o3d
import numpy as np
import re


def create_rectangle():
    # Define the coordinates of the rectangle
    points = [
        [-11.1, 5.5, 0.0],  # Point 1
        [9.6, 5.5, 0.0],  # Point 2
        [9.6, -4.42, 0.0],  # Point 3
        [-11.1, -4.42, 0.0]  # Point 4
    ]

    # Define the lines connecting the points
    lines = [
        [0, 1],  # Line from Point 1 to Point 2
        [1, 2],  # Line from Point 2 to Point 3
        [2, 3],  # Line from Point 3 to Point 4
        [3, 0]  # Line from Point 4 to Point 1
    ]

    # Create a line set
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    line_set.lines = o3d.utility.Vector2iVector(lines)

    # Set the color of the lines (red)
    line_set.colors = o3d.utility.Vector3dVector([[1, 0, 0] for _ in lines])

    # Create a bounding box to simulate line width in x-direction
    boxes = []
    for line in lines:
        p1 = np.array(points[line[0]])
        p2 = np.array(points[line[1]])
        direction = p2 - p1
        length = np.linalg.norm(direction)
        direction /= length

        # Create a box for each line segment
        box = o3d.geometry.TriangleMesh.create_box(width=length, height=0.1, depth=0.01)
        box.translate(p1)
        rotation_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle(
            [0, 0, np.arctan2(direction[1], direction[0])]
        )
        box.rotate(rotation_matrix, center=p1)
        box.paint_uniform_color([1, 0, 0])
        boxes.append(box)

    return [line_set] + boxes


def create_grid():
    # Create a grid on the x-y plane
    grid = o3d.geometry.LineSet()
    grid_points = []
    grid_lines = []
    grid_color = []

    size = 20  # Grid size
    step = 1  # Grid step

    for x in range(-size, size + 1, step):
        grid_points.append([x, -size, 0])
        grid_points.append([x, size, 0])
        grid_lines.append([len(grid_points) - 2, len(grid_points) - 1])
        grid_color.append([0.5, 0.5, 0.5])

    for y in range(-size, size + 1, step):
        grid_points.append([-size, y, 0])
        grid_points.append([size, y, 0])
        grid_lines.append([len(grid_points) - 2, len(grid_points) - 1])
        grid_color.append([0.5, 0.5, 0.5])

    grid.points = o3d.utility.Vector3dVector(grid_points)
    grid.lines = o3d.utility.Vector2iVector(grid_lines)
    grid.colors = o3d.utility.Vector3dVector(grid_color)

    return grid


def create_origin():
    # Create coordinate axes to indicate the origin
    origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
    return origin


# Function to visualize 3D point cloud with bounding box
def visualize_with_bounding_box(prediction_file, points_file):
    # Load the point cloud data
    points = np.load(points_file)

    # Debug: print the shape of the points array
    print(f"Shape of points array: {points.shape}")

    # Ensure points are of shape (N, 3) and type float64
    if points.shape[1] != 3:
        # If there are more than 3 columns, take only the first 3 columns (x, y, z)
        points = points[:, :3]
        print("Using only the first 3 columns (x, y, z).")

    points = points.astype(np.float64)  # Make sure the points are of type float64

    # Filter out points with negative z-coordinates
    points = points[points[:, 2] >= 0]


    # Create an Open3D point cloud object
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    # Load the prediction data from txt file
    with open(prediction_file, 'r') as f:
        data = f.read().splitlines()

    # Parse the prediction data
    prediction = {}
    for line in data:
        if line.startswith("frame_id"):
            frame_id = line.split(":")[1].strip().strip("[]'")
        if line.startswith("boxes_lidar"):
            # The boxes_lidar data might be multi-line; handle this by parsing manually
            box_str = line.split(":")[1].strip()

            # Clean up the box string to remove extra brackets and whitespace
            box_str = re.sub(r'[\[\]]', '', box_str)  # Remove square brackets
            box_str = re.sub(r'\s+', ' ', box_str)  # Replace multiple spaces with a single space

            # Split the box string into individual values
            try:
                # Manually split the values based on spaces, then convert to float
                box_values = [float(val) for val in box_str.split() if val]

                # Convert the list to a numpy array
                box = np.array(box_values).reshape(1, -1)

            except Exception as e:
                print(f"Error parsing bounding box data: {e}")
                return

        if line.startswith("score"):
            score = np.array(eval(line.split(":")[1].strip()))
        if line.startswith("pred_labels"):
            label = np.array(eval(line.split(":")[1].strip()))

    # Extracting bounding box details
    if len(box) > 0:
        # Handle case where only 6 values are present (without heading_angle)
        if len(box[0]) == 6:
            x, y, z, dx, dy, dz = box[0]
            heading_angle = 0  # Assigning a default value for heading angle
        elif len(box[0]) == 7:
            x, y, z, dx, dy, dz, heading_angle = box[0]
        else:
            print("Unexpected box data format.")
            return

        # Create a box mesh (axis-aligned bounding box)
        bbox = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=np.array([x - dx / 2, y - dy / 2, z - dz / 2]),
            max_bound=np.array([x + dx / 2, y + dy / 2, z + dz / 2])
        )

        # Create a mesh from bounding box
        bbox_color = [0, 1, 0]  # Green color
        bbox_lines = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(bbox)
        bbox_lines.paint_uniform_color(bbox_color)

        # Add the class name and score as text annotations
        class_name = f"Class: {label[0]}"  # Assuming 'label' contains the class ID
        score_text = f"Score: {score[0]:.2f}"  # Assuming 'score' is a float

        # Create text geometries for class name and score
        # We are using placeholder text for now, as Open3D does not natively support 3D text rendering
        print(f"Class: {label[0]}, Score: {score[0]:.2f}")

    return [point_cloud, bbox_lines]

def create_additional_origin():
    # Create a coordinate frame for the additional origin
    additional_origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
    additional_origin.translate([-5.505, -4.787, 1.557])
    return additional_origin


# Create the rectangle, grid, and origin
rectangle = create_rectangle()
grid = create_grid()
origin = create_origin()
additional_origin = create_additional_origin()

# Load the point cloud and bounding box
prediction_file = "/home/dartagnan-dev/sahil-dev/Results/OpenPCdet/Radar_Static/txt_results/prediction_001557.txt"
points_file = "/home/dartagnan-dev/sahil-dev/Results/OpenPCdet/Radar_Static/points/008197.npy"
bbox_and_pointcloud = visualize_with_bounding_box(prediction_file, points_file)

# Visualize everything together
o3d.visualization.draw_geometries(rectangle + [grid, origin, additional_origin] + bbox_and_pointcloud)