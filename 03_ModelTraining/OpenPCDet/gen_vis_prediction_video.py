import open3d as o3d
import numpy as np
import re
import os
import time
import cv2  # Import OpenCV

def create_rectangle():
    points = [
        [-11.1, 5.5, 0.0], [9.6, 5.5, 0.0],
        [9.6, -4.42, 0.0], [-11.1, -4.42, 0.0]
    ]
    lines = [[0, 1], [1, 2], [2, 3], [3, 0]]
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    line_set.lines = o3d.utility.Vector2iVector(lines)
    line_set.colors = o3d.utility.Vector3dVector([[1, 0, 0] for _ in lines])

    boxes = []
    for line in lines:
        p1, p2 = np.array(points[line[0]]), np.array(points[line[1]])
        direction = p2 - p1
        length = np.linalg.norm(direction)
        direction /= length
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
    grid = o3d.geometry.LineSet()
    grid_points, grid_lines, grid_color = [], [], []
    size, step = 20, 1
    for x in range(-size, size + 1, step):
        grid_points.extend([[x, -size, 0], [x, size, 0]])
        grid_lines.append([len(grid_points) - 2, len(grid_points) - 1])
        grid_color.append([0.5, 0.5, 0.5])
    for y in range(-size, size + 1, step):
        grid_points.extend([[-size, y, 0], [size, y, 0]])
        grid_lines.append([len(grid_points) - 2, len(grid_points) - 1])
        grid_color.append([0.5, 0.5, 0.5])
    grid.points = o3d.utility.Vector3dVector(grid_points)
    grid.lines = o3d.utility.Vector2iVector(grid_lines)
    grid.colors = o3d.utility.Vector3dVector(grid_color)
    return grid

def create_origin():
    return o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])

def create_additional_origin():
    additional_origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
    additional_origin.translate([-5.505, -4.787, 1.557])
    return additional_origin

def visualize_with_bounding_box(prediction_file, points_file):
    # Define rectangle boundaries
    x_min, x_max = -10.4, 9.6
    y_min, y_max = -4.42, 5.5

    points = np.load(points_file)
    points = points[:, :3].astype(np.float64)

    # Filter points inside the rectangle (x and y directions)
    points = points[(points[:, 0] >= x_min) & (points[:, 0] <= x_max) &
                    (points[:, 1] >= y_min) & (points[:, 1] <= y_max)]

    points = points[points[:, 2] >= 0]  # Retain points with z >= 0
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    with open(prediction_file, 'r') as f:
        data = f.read().splitlines()

    prediction = {}
    box = None
    heading_angle = 0

    for idx, line in enumerate(data):
        if line.startswith("frame_id"):
            frame_id = line.split(":")[1].strip().strip("[]'")
        if line.startswith("boxes_lidar"):
            box_str = re.sub(r'[\[\]]', '', line.split(":")[1].strip())
            box_str = re.sub(r'\s+', ' ', box_str)
            # Check for the next line if the box_str is incomplete
            if idx + 1 < len(data) and not data[idx + 1].startswith(("score", "pred_labels", "frame_id")):
                box_str += " " + re.sub(r'[\[\]]', '', data[idx + 1].strip())
            try:
                box_values = [float(val) for val in box_str.split() if val]
                box = np.array(box_values).reshape(1, -1)
            except Exception as e:
                print(f"Error parsing bounding box data: {e}")
                return
        if line.startswith("score"):
            score = np.array(eval(line.split(":")[1].strip()))
        if line.startswith("pred_labels"):
            label = np.array(eval(line.split(":")[1].strip()))

    if box is not None and len(box[0]) >= 6:
        if len(box[0]) == 6:
            x, y, z, dx, dy, dz = box[0][:6]
            heading_angle = 0  # Default to 0 if no heading angle
        elif len(box[0]) == 7:
            x, y, z, dx, dy, dz, heading_angle = box[0]
        else:
            print("Unexpected box data format.")
            return

        # Apply an additional 90-degree rotation to the heading angle
        additional_rotation = np.pi / 2  # 90 degrees in radians
        heading_angle += additional_rotation

        # Create OrientedBoundingBox for heading_angle
        center = np.array([x, y, z])
        extents = np.array([dx, dy, dz])
        rotation_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle([0, 0, heading_angle])

        oob = o3d.geometry.OrientedBoundingBox(center=center, R=rotation_matrix, extent=extents)
        oob.color = [0, 1, 0]  # Green for visualization

        print(f"Class: {label[0]}, Score: {score[0]:.2f}")

    return [point_cloud, oob]

def update_visualization(prediction_folder, points_folder):
    rectangle = create_rectangle()
    grid = create_grid()
    origin = create_origin()
    additional_origin = create_additional_origin()

    prediction_files = sorted([f for f in os.listdir(prediction_folder) if f.endswith('.txt')])
    vis = o3d.visualization.Visualizer()
    vis.create_window()

    for pred_file in prediction_files:
        pred_path = os.path.join(prediction_folder, pred_file)

        with open(pred_path, 'r') as f:
            for line in f:
                if line.startswith('frame_id'):
                    frame_id = line.split(':')[1].strip().strip("[]'")
                    break

        point_file = f"{frame_id}.npy"
        point_path = os.path.join(points_folder, point_file)

        if os.path.exists(point_path):
            bbox_and_pointcloud = visualize_with_bounding_box(pred_path, point_path)

            vis.clear_geometries()
            for geom in rectangle + [grid, origin, additional_origin] + bbox_and_pointcloud:
                vis.add_geometry(geom)

            vis.poll_events()
            vis.update_renderer()

            time.sleep(0.2)  # 5 FPS

    vis.destroy_window()

if __name__ == "__main__":
    prediction_folder = "/home/dartagnan-dev/sahil-dev/Results/OpenPCdet/Radar_dynamic/txt_results"
    points_folder = "/home/dartagnan-dev/sahil-dev/Results/OpenPCdet/Radar_dynamic/points"
    update_visualization(prediction_folder, points_folder)
