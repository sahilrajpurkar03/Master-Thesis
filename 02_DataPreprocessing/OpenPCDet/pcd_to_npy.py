import os
import numpy as np
import open3d as o3d

def pcd_to_npy(pcd_file, npy_file):
    # Read the .pcd file using Open3D
    pcd = o3d.io.read_point_cloud(pcd_file)
    points = np.asarray(pcd.points)

    # Add dummy intensity column (zeros)
    intensities = np.zeros((points.shape[0], 1), dtype=np.float32)
    points_with_intensity = np.hstack((points, intensities))

    # Save to .npy
    np.save(npy_file, points_with_intensity)
    print(f"Saved: {npy_file}")

def process_pcd_folder(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    pcd_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.pcd')])

    for filename in pcd_files:
        input_path = os.path.join(input_dir, filename)
        output_filename = filename.replace('.pcd', '.npy')
        output_path = os.path.join(output_dir, output_filename)

        print(f"Processing: {input_path} -> {output_path}")
        pcd_to_npy(input_path, output_path)

# Example usage
input_dir = r'E:\your\path\to\pcd\files'
output_dir = r'E:\your\path\to\npy\output'
process_pcd_folder(input_dir, output_dir)
