"""
Assign stable IDs to segmented egg instances using a robust grid-sorting approach.
"""

import numpy as np

from scripts.logger import setup_logger
logger = setup_logger(__name__)

def compute_centroid(mask: np.ndarray) -> np.ndarray:
    coords = np.argwhere(mask)
    if coords.size == 0:
        logger.error("Attempted to compute centroid for an empty mask.")
        raise ValueError("Cannot compute centroid of empty mask.")

    return coords.mean(axis=0)


def assign_ids(instances: dict[int, np.ndarray], row_tolerance: int = 50) -> dict[int, np.ndarray]:
    """
    Assign stable IDs using a robust grid-sorting approach.
    Clusters centroids into rows before sorting horizontally to prevent ID swapping.
    """
    logger.info(f"Starting ID assignment for {len(instances)} instances.")

    instance_data = []
    for _, mask in instances.items():
        centroid = compute_centroid(mask)
        instance_data.append({"mask": mask, "centroid": centroid})

    # Sort by Y first to identify rows
    instance_data.sort(key=lambda x: x["centroid"][1])

    # Divide into rows based on a Y-coordinate threshold
    # and sort eggs within each row by X-coordinate.
    final_ordered = []
    current_row = []

    for i, item in enumerate(instance_data):
        if not current_row:
            current_row.append(item)
        else:
            # If current egg is vertically close to the row's average Y, it's the same row
            avg_y = np.mean([x["centroid"][1] for x in current_row])
            if abs(item["centroid"][1] - avg_y) < row_tolerance:
                current_row.append(item)
            else:
                # Row is finished, sort it by X and add to final list
                current_row.sort(key=lambda x: x["centroid"][2])
                final_ordered.extend(current_row)
                current_row = [item]

    current_row.sort(key=lambda x: x["centroid"][2])
    final_ordered.extend(current_row)
    logger.info(f"Successfully clustered and sorted {len(final_ordered)} eggs.")

    return {i + 1: data["mask"] for i, data in enumerate(final_ordered)}


def crop_volume(volume: np.ndarray, mask: np.ndarray, padding: int = 5) -> np.ndarray:
    """
    Crop 3D volume to bounding box with safe boundary checks.
    """
    coords = np.argwhere(mask)

    if coords.size == 0:
        logger.error("Crop requested on an empty mask.")
        raise ValueError("Cannot crop empty mask.")

    # floor/ceil
    z_min, y_min, x_min = np.floor(coords.min(axis=0) - padding).astype(int)
    z_max, y_max, x_max = np.ceil(coords.max(axis=0) + padding).astype(int)

    shape = volume.shape
    # Boundary clamping to prevent IndexError
    crop = volume[
        max(0, z_min):min(shape[0], z_max),
        max(0, y_min):min(shape[1], y_max),
        max(0, x_min):min(shape[2], x_max)
    ]
    logger.debug(f"Cropped volume shape: {crop.shape}")
    return crop

