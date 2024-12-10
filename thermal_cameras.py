import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import zoom, gaussian_filter, sobel

# Configuration
NUM_IMAGES = 26
SAVE_DIR = "dataset"
CMAP = 'inferno'
VMIN = 20.0
VMAX = 25.0
TARGET_SIZE = (1024, 1024)

# Ensure the save directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Initialize Sensor
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
thermal_camera = adafruit_mlx90640.MLX90640(i2c)
thermal_camera.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ

# Initialize frame buffer
frame = np.zeros((24 * 32,), dtype=np.float32)

# Calculate upscaling factors for each dimension
upscale_factor_x = TARGET_SIZE[0] / 32
upscale_factor_y = TARGET_SIZE[1] / 24

def average_frames(frames):
    return np.mean(np.array(frames), axis=0)

frames_to_average = 5
frame_buffer = []


def save_frames(n_imgs):
    for i in range(n_imgs): 
        try: 
            thermal_camera.getFrame(frame) 
            data_array = np.reshape(frame, (24, 32)) 
            
            # Store frames for averaging 
            frame_buffer.append(data_array) 
            if len(frame_buffer) > frames_to_average: 
                frame_buffer.pop(0) # Remove the oldest frame 
                
            # Calculate the average of the frames 
            if len(frame_buffer) == frames_to_average: 
                avg_array = average_frames(frame_buffer) 
                upscaling_array = zoom(avg_array, (upscale_factor_y, upscale_factor_x), order=3) 
                filename = os.path.join(SAVE_DIR, f"average_frame_label_2_{i:02d}.png") 
                plt.imsave(filename, upscaling_array, cmap=CMAP, vmin=VMIN, vmax=VMAX) 
                print(f"Saved {filename}")
        except ValueError: 
            print("Frame read error, skipping.")
    print("Dataset image capture complete!")

save_frames(NUM_IMAGES)
