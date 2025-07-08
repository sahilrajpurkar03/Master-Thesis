import json
import open3d as o3d
import numpy as np
import os

# Input and output file paths
input_txt = r'E:\your\path\to\file.txt'  # Replace with your actual input file path
output_folder = r'E:\your\path\to\pcd\output' # Replace with your desired output folder path 

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

def process_txt_to_pcd(input_file, output_folder):
    # Extract the base name of the input file (without extension)
    input_file_name = os.path.splitext(os.path.basename(input_file))[0]

    with open(input_file, "r") as file:
        for line_num, line in enumerate(file):
            if line.strip():  # Ensure the line is not empty
                frame_data = json.loads(line)  # Parse the JSON line
                x = frame_data.get("x", [])
                y = frame_data.get("y", [])
                z = frame_data.get("z", [])

                # Combine x, y, z into a numpy array
                points = np.array([x, y, z]).T  # Transpose to shape (n, 3)

                # Create Open3D point cloud object
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(points)

                # Create the output file name: <input_file_name>_frame_<frame_number>.pcd
                output_file_name = f"{input_file_name}_frame_{line_num:04d}.pcd"
                output_path = os.path.join(output_folder, output_file_name)

                # Save as .pcd file
                o3d.io.write_point_cloud(output_path, pcd)
                print(f"Saved frame {line_num} to {output_path}")

# Process the file
process_txt_to_pcd(input_txt, output_folder)
