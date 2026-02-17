"""
Segmentation using Otsu thresholding to extract instance segments.
"""

import numpy as np
from scipy.ndimage import gaussian_filter, label
from skimage.morphology import opening, ball
from skimage.filters import threshold_otsu

from scripts.logger import setup_logger
logger = setup_logger(__name__)


def preprocess(volume: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """ Normalize intensities and apply Gaussian smoothing. """

    v_min, v_max = np.percentile(volume, (1, 99))
    logger.info(f"Normalizing volume: min_perc={v_min}, max_perc={v_max}")

    if v_max - v_min < 1e-6:
        logger.error("Volume intensity range is too small for normalization.")
        raise ValueError("Volume intensity range is too small for normalization.")

    normalized = np.clip((volume - v_min) / (v_max - v_min), 0, 1)
    logger.debug(f"Applying Gaussian smoothing with sigma={sigma}")
    return gaussian_filter(normalized, sigma=sigma)


def segment_foreground(volume: np.ndarray) -> np.ndarray:
    """ Segment eggs using Otsu thresholding and morphological cleaning. """

    threshold = threshold_otsu(volume)
    logger.info(f"Otsu threshold calculated: {threshold}")

    mask = volume > threshold

    # Clean small noise
    logger.debug("Performing morphological opening with ball(2)")
    mask = opening(mask, ball(2))

    if np.sum(mask) == 0:
        logger.error("Segmentation failed: Foreground mask is empty")
        raise RuntimeError("Segmentation failed: no foreground detected.")

    logger.info(f"Foreground segmentation successful")
    return mask


def extract_instances(mask: np.ndarray, expected_count: int = 12) -> dict[int, np.ndarray]:
    """ Extract instance segmentation results. """
    labeled_volume, num_instances = label(mask)
    logger.info(f"Connected component labeling found {num_instances} raw instances")

    if num_instances == 0:
        logger.error("No connected components found in mask")
        raise RuntimeError("No connected components detected.")

    # Calculate sizes once using np.bincount
    # index 0 is background, so skip it
    sizes = np.bincount(labeled_volume.ravel())

    # Get indices of the largest objects (excluding background at index 0)
    # and take top_k indices based on their size in the 'sizes' array
    largest_indices = np.argsort(sizes[1:])[::-1][:expected_count] + 1

    filtered = {
        i + 1: (labeled_volume == idx)
        for i, idx in enumerate(largest_indices)
    }

    if len(filtered) < expected_count:
        logger.warning(f"Detection mismatch: Only {len(filtered)} eggs detected (expected {expected_count})")
    else:
        logger.info(f"Successfully extracted the {expected_count} largest instances")

    return filtered

