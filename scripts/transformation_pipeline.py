"""
End-to-end pipeline that transforms a 3D tray MRI scan into individual 3D egg volumes.
"""

import numpy as np
from scripts.segmentation import preprocess, segment_foreground, extract_instances
from scripts.labeling import assign_ids, crop_volume

from scripts.logger import setup_logger
logger = setup_logger(__name__)


class TransformationPipeline:
    def __init__(self, sigma: float = 1.0, expected_egg_count: int = 12, row_tolerance: int = 50):
        self.sigma = sigma
        self.expected_egg_count = expected_egg_count
        self.row_tolerance = row_tolerance
        logger.info(f"TransformationPipeline initialized")

    def validate_input(self, volume: np.ndarray) -> None:
        """ Checks for data quality issues that load_nifti doesn't catch. """

        logger.info("Validating input volume")

        if np.isnan(volume).any():
            logger.error("Input contains NaN values")
            raise ValueError("Input volume contains NaN values.")

        if np.max(volume) - np.min(volume) < 1e-6:
            logger.error("Volume intensity range too small")
            raise ValueError("Volume intensity range too small.")

        logger.info("Input validation successful")

    def run(self, volume: np.ndarray) -> dict[int, np.ndarray]:
        logger.info("Starting transformation pipeline")
        self.validate_input(volume)

        # Preprocess
        logger.info("Preprocessing volume")
        processed = preprocess(volume, self.sigma)

        # Segment
        logger.info("Segmenting foreground")
        mask = segment_foreground(processed)

        # Instance Extraction
        logger.info("Extracting connected components")
        instances = extract_instances(mask, self.expected_egg_count)

        if len(instances) == 0:
            logger.error("No eggs detected after segmentation")
            raise RuntimeError("No eggs detected.")

        if len(instances) != self.expected_egg_count:
            logger.warning(f"Expected 12 eggs but found {len(instances)}")

        # ID Assignment & Cropping
        logger.info("Assigning stable IDs")
        labeled_masks = assign_ids(instances, self.row_tolerance)

        # Cropping
        logger.info("Cropping individual egg volumes")
        results = {
            egg_id: crop_volume(volume, egg_mask)
            for egg_id, egg_mask in labeled_masks.items()
        }
        logger.info(f"Pipeline completed. Extracted {len(results)} eggs.")

        return results

