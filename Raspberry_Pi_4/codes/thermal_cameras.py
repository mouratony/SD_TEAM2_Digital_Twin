import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
import matplotlib.colors as mcolors
import matplotlib.animation as animation
import time
from PIL import Image
import io

# Configuration
NUM_IMAGES = 20
SAVE_DIR = "dataset"
VMIN = 25.0
VMAX = 32.0
TARGET_SIZE = (24, 32)  # (height, width)

os.makedirs(SAVE_DIR, exist_ok=True)

# Load ML model
try:
    model = tf.keras.models.load_model('DATH_model-V0.keras')
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Initialize Thermal Camera Sensor
try:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    thermal_camera = adafruit_mlx90640.MLX90640(i2c, address=0x33)
    thermal_camera.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
except Exception as e:
    print(f"Error initializing thermal camera: {e}")
    thermal_camera = None

# Frame buffer for averaging (used in saving images)
frame = np.zeros((24 * 32,), dtype=np.float32)
frames_to_average = 5
frame_buffer = []

# Define a custom colormap (the same one used during training)
colors = [(0, 'black'), (0.2, 'darkred'), (0.3, 'red'), (0.4, 'orange'), (1, 'yellow')]
cm = mcolors.LinearSegmentedColormap.from_list('custom_heatmap', colors)

# Set up the live display figure
fig, ax = plt.subplots(figsize=[16, 12])
# Initialize with a blank image; note that display images will be in float32 [0,1]
thermal_image = ax.imshow(np.zeros((TARGET_SIZE[0], TARGET_SIZE[1], 3)), interpolation='bicubic', vmin=0, vmax=1)
cbar = fig.colorbar(thermal_image)
cbar.set_label('Normalized Intensity', rotation=270, labelpad=20)
ax.set_xticks([])
ax.set_yticks([])

def apply_colormap(thermal_data, cmap_obj, vmin, vmax):
    """
    Apply the custom colormap in a vectorized way.
    thermal_data: 2D array of raw thermal values.
    Returns an RGB image (uint8) with shape (H, W, 3).
    """
    # Normalize data to [0, 1]
    norm_data = (thermal_data - vmin) / (vmax - vmin)
    norm_data = np.clip(norm_data, 0, 1)
    # Apply the colormap (this returns an RGBA image with values in [0,1])
    colored = cmap_obj(norm_data)
    # Drop alpha channel and convert to uint8
    colored = (colored[..., :3] * 255).astype(np.uint8)
    return colored

def preprocess_image(thermal_image_data):
    """
    Process raw thermal data to match the training image style.
    1. Apply the custom colormap using a fast, vectorized function.
    2. Resize using PIL if the size differs (for consistency with training).
    3. Normalize to [0, 1] and add a batch dimension.
    """
    # Apply colormap (expected output shape: (24, 32, 3) if input is 24x32)
    color_mapped_image = apply_colormap(thermal_image_data, cm, VMIN, VMAX)
    
    # Ensure the image size matches TARGET_SIZE
    if color_mapped_image.shape[0:2] != TARGET_SIZE:
        pil_img = Image.fromarray(color_mapped_image)
        pil_img = pil_img.resize((TARGET_SIZE[1], TARGET_SIZE[0]), Image.LANCZOS)
        color_mapped_image = np.array(pil_img)
    
    # Normalize to [0, 1]
    color_mapped_image = color_mapped_image.astype(np.float32) / 255.0
    # Expand dims to create a batch of 1 (shape: (1, height, width, 3))
    return np.expand_dims(color_mapped_image, axis=0)

def predict_people_count(thermal_image_data):
    """
    Predict the number of people by processing the thermal data
    and using the trained ML model.
    """
    if model:
        input_tensor = preprocess_image(thermal_image_data)   # shape (1, 24, 32, 3)
        prediction = model.predict(input_tensor, verbose=0)   # shape (1, num_classes)
        predicted_class = np.argmax(prediction, axis=1)[0]      # choose the class with highest probability
        return predicted_class
    else:
        return 0

def average_frames(frames):
    return np.mean(np.array(frames), axis=0)

def save_frames(n_imgs):
    """
    Capture and save images from the thermal camera.
    Averaging a few frames can help reduce noise.
    """
    if not thermal_camera:
        print("Thermal camera not initialized.")
        return
    for i in range(n_imgs):
        try:
            thermal_camera.getFrame(frame)
            data_array = np.reshape(frame, (24, 32))
            frame_buffer.append(data_array)
            if len(frame_buffer) > frames_to_average:
                frame_buffer.pop(0)
            if len(frame_buffer) == frames_to_average:
                avg_array = average_frames(frame_buffer)
                filename = os.path.join(SAVE_DIR, f"new_frame_label_1_000{i:02d}.png")
                plt.imsave(filename, avg_array, cmap=cm, vmin=VMIN, vmax=VMAX)
                print(f"Saved {filename}")
        except ValueError:
            print("Frame read error, skipping.")
    print("Dataset image capture complete!")

def update_frame_func(frame_number):
    """
    This function is called repeatedly by the animation.
    It captures a new frame, processes it, updates the prediction,
    and refreshes the displayed image.
    """
    if not thermal_camera:
        print("Thermal camera not initialized.")
        return [thermal_image]
    try:
        thermal_camera.getFrame(frame)
        raw_data = np.reshape(frame, (24, 32))
        # Preprocess raw data for both prediction and display
        processed_image = preprocess_image(raw_data)  # shape (1, 24, 32, 3)
        display_img = processed_image[0]  # Remove batch dimension; values in [0,1]
        
        # Get prediction using the processed image
        people_count = np.argmax(model.predict(processed_image, verbose=0), axis=1)[0]
        ax.set_title(f"People Count: {people_count}")
        
        # Update the displayed image
        thermal_image.set_data(display_img)
        thermal_image.set_clim(0, 1)
        cbar.update_normal(thermal_image)
        return [thermal_image]
    except ValueError as e:
        print(f"Frame read error: {e}")
        return [thermal_image]
    except Exception as e:
        print(f"Unexpected error: {e}")
        return [thermal_image]

def main():
    try:
        s = int(input("Choose an action:\n(1) Save Thermal Images\t(2) Live CAM\n>>> "))
        if s == 1:
            save_frames(NUM_IMAGES)
        elif s == 2:
            # Adjust the interval to match the sensor refresh rate (e.g., 500ms for 2Hz)
            ani = animation.FuncAnimation(fig, update_frame_func, interval=500, blit=False, save_count=1000)
            plt.show()
        else:
            print("Invalid choice. Exiting.")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    main()
