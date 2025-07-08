import os
import json
import numpy as np
import matplotlib.pyplot as plt

def load_radar_data(file_name):
    """Load radar data from the input file and return all readings."""
    data_list = []
    try:
        with open(file_name, 'r') as file:
            for line in file:
                data = json.loads(line.strip())
                data_list.append(data)
        return data_list
    except Exception as e:
        print(f"Error loading or parsing file {file_name}: {e}")
        return []

def create_heatmap(range_data, azimuth_data, output_path, xlim=(-70, 70), ylim=(0, 6.5)):
    """Create and save a 2D histogram heatmap from range and azimuth data with zoomed out limits."""
    plt.figure(figsize=(10, 8))
    
    # Corrected range format for plt.hist2d
    plt.hist2d(azimuth_data, range_data, bins=[100, 100], cmap='viridis', range=[xlim, ylim])
    
    plt.colorbar(label='Count')
    plt.title('Range vs Azimuth 2D Histogram')
    plt.xlabel('Azimuth (degrees)')
    plt.ylabel('Range (meters)')
    
    # Set limits to zoom out
    plt.xlim(xlim)
    plt.ylim(ylim)

    # Save the plot
    plt.savefig(output_path, dpi=300)
    plt.close()

def process_and_save_heatmaps(input_file, output_dir):
    """Process the radar data and save heatmaps for each timestamp."""
    radar_data = load_radar_data(input_file)
    
    # Create a folder named after the input file (without extension)
    file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_folder = os.path.join(output_dir, file_name)
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over each reading and create heatmaps
    for i, reading in enumerate(radar_data):
        range_data = reading['range']
        azimuth_data = reading['azimuth']
        output_path = os.path.join(output_folder, f'frame{i+1:04d}_{file_name}.jpg')  # frame01.jpg, frame02.jpg, ...
        
        create_heatmap(range_data, azimuth_data, output_path)
        print(f"Saved heatmap for frame {i+1} to {output_path}")

def main():
    # Hard-coded settings with corrected file paths
    input_file = r'E:\your\path\to\file.txt'  # Replace with your actual input file path
    output_dir = 'E:\your\path\to\Range-Azimuth-2D-Histogram\output'  # Replace with your desired output directory path

    # Process and save heatmaps
    process_and_save_heatmaps(input_file, output_dir)
    print("All heatmaps have been generated and saved.")

if __name__ == "__main__":
    main()
