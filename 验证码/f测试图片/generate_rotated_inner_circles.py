import cv2
import numpy as np
import argparse
import os

def generate_rotated_images(
    image_path,
    inner_diameter,
    output_folder="rotated_images",
    rotation_step=1,
):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image from {image_path}")
        return

    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    inner_radius = inner_diameter // 2

    # Ensure inner circle fits within the image
    if not (center[0] - inner_radius >= 0 and center[0] + inner_radius <= w and
            center[1] - inner_radius >= 0 and center[1] + inner_radius <= h):
        print("Error: Inner circle diameter is too large for the image dimensions or center is off.")
        return

    # Create mask for the inner circle
    inner_circle_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(inner_circle_mask, center, inner_radius, 255, -1)

    # Create mask for the outer ring (everything outside the inner circle)
    outer_ring_mask = cv2.bitwise_not(inner_circle_mask)

    # Extract the outer ring region from the original image
    outer_ring_region = cv2.bitwise_and(img, img, mask=outer_ring_mask)

    # Extract the inner circle content as a square crop
    x_start = center[0] - inner_radius
    y_start = center[1] - inner_radius
    cropped_inner_content = img[y_start : y_start + inner_diameter, x_start : x_start + inner_diameter].copy()

    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    num_rotations = 360 // rotation_step
    print(f"Generating {num_rotations} images with rotated inner circles (step: {rotation_step} degrees)...")

    for i in range(num_rotations):
        angle = i * rotation_step

        # Rotate the cropped inner content
        M = cv2.getRotationMatrix2D((inner_diameter // 2, inner_diameter // 2), angle, 1)
        rotated_inner_content = cv2.warpAffine(cropped_inner_content, M, (inner_diameter, inner_diameter))

        # Create a temporary mask for pasting the rotated inner content
        temp_inner_circle_mask = np.zeros((inner_diameter, inner_diameter), dtype=np.uint8)
        cv2.circle(temp_inner_circle_mask, (inner_diameter // 2, inner_diameter // 2), inner_radius, 255, -1)

        # Apply the temporary mask to the rotated inner content
        rotated_inner_content_masked = cv2.bitwise_and(rotated_inner_content, rotated_inner_content, mask=temp_inner_circle_mask)

        # Create a full-sized image for the rotated inner content, positioned correctly
        full_rotated_inner_content_canvas = np.zeros_like(img)
        full_rotated_inner_content_canvas[y_start : y_start + inner_diameter, x_start : x_start + inner_diameter] = rotated_inner_content_masked

        # Combine the outer ring and the rotated inner circle
        final_image = cv2.add(outer_ring_region, full_rotated_inner_content_canvas)

        # Save the image
        output_path = os.path.join(output_folder, f"rotated_image_{int(angle):03d}deg.png")
        cv2.imwrite(output_path, final_image)
        print(f"Saved: {output_path}")

    print(f"Successfully generated rotated images in '{output_folder}' folder.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates multiple images by rotating the inner circle while keeping the outer ring static.")
    parser.add_argument('--image', type=str, required=True, help='Path to the input image file.')
    parser.add_argument('--inner_diameter', type=int, default=261, help='Diameter of the inner circle.')
    parser.add_argument('--output_folder', type=str, default="rotated_images", help='Folder to save the generated images.')
    parser.add_argument('--rotation_step', type=int, default=1, help='Rotation step in degrees (e.g., 1 for every 1 degree).')
    
    args = parser.parse_args()

    generate_rotated_images(
        args.image,
        args.inner_diameter,
        args.output_folder,
        args.rotation_step,
    )