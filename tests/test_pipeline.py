"""
Unit and Integration tests for the Egg Transformation Pipeline.
These tests use synthetic data to verify logic without requiring large MRI files.
"""

import pytest
import numpy as np
from scripts.transformation_pipeline import TransformationPipeline
from scripts.labeling import assign_ids, crop_volume
from scripts.segmentation import preprocess


@pytest.fixture
def mock_volume():
    """Creates a synthetic 3D volume with a LARGE enough egg for percentiles."""
    vol = np.zeros((50, 50, 50), dtype=np.float32)
    # Create a large block so 99th percentile is not 0
    vol[10:40, 10:40, 10:40] = 1.0
    return vol


# UNIT TESTS
def test_preprocess_normalization(mock_volume):
    """Verify that intensities are scaled between 0 and 1."""
    processed = preprocess(mock_volume, sigma=1.0)
    assert processed.max() <= 1.0
    assert processed.min() >= 0.0

def test_crop_volume_dimensions():
    """Ensure cropping returns the correct sub-volume shape."""
    vol = np.random.rand(50, 50, 50)
    mask = np.zeros_like(vol)
    mask[10:20, 10:20, 10:20] = 1
    cropped = crop_volume(vol, mask, padding=2)
    assert cropped.shape == (14, 14, 14) or cropped.shape == (13, 13, 13)

def test_assign_ids_sorting():
    """Verify grid-sorting logic."""
    mask1 = np.zeros((50, 50, 50))
    mask1[10:15, 10:15, 5:10] = 1
    mask2 = np.zeros((50, 50, 50))
    mask2[10:15, 10:15, 20:25] = 1

    instances = {1: mask2, 2: mask1}
    ordered = assign_ids(instances, row_tolerance=10)
    assert np.array_equal(ordered[1], mask1)


# EDGE CASE TESTS
def test_pipeline_invalid_input():
    pipeline = TransformationPipeline()
    bad_vol = np.array([[[np.nan]]])
    with pytest.raises(ValueError):
        pipeline.validate_input(bad_vol)


# INTEGRATION TEST
def test_full_pipeline_run(mock_volume):
    """Test the entire pipeline."""
    # Use a volume where the 'egg' is big enough for percentiles
    pipeline = TransformationPipeline(expected_egg_count=1)
    results = pipeline.run(mock_volume)

    assert len(results) == 1
    egg_id = list(results.keys())[0]
    assert results[egg_id].sum() > 0
