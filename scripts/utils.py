"""
Utility for loading and saving 3D MRI volumes.
Handles basic validation and filesystem safety.
"""

from pathlib import Path
import numpy as np
import nibabel as nib
from nibabel.filebasedimages import ImageFileError

from scripts.logger import setup_logger
logger = setup_logger(__name__)


def load_nifti(path: str | Path) -> np.ndarray:
    """
    Load a NIfTI file from disk and return the image data as a numpy array.

    :param path: Path to the input NIfTI file.
    :return: 3D numpy array representing the MRI volume.
    """
    path = Path(path)
    logger.info(f"Loading NIfTI file from: {path}")

    if not path.exists():
        logger.error(f"NIfTI file not found: {path}")
        raise FileNotFoundError(f"NIfTI file not found: {path}")

    try:
        image = nib.load(str(path))
        volume = image.get_fdata()
    except ImageFileError:
        logger.error(f"Invalid or corrupted NIfTI file: {path}")
        raise ValueError(f"File at {path} is not a valid NIfTI or is corrupted.")
    except MemoryError:
        logger.error(f"System memory exceeded while loading: {path}")
        raise MemoryError(f"Volume at {path} is too large for system RAM.")
    except Exception as e:
        logger.error(f"Unexpected error loading {path}: {e}")
        raise RuntimeError(f"Unexpected error loading {path}: {e}")

    if volume.ndim != 3:
        logger.error(f"Dimension mismatch: Expected 3D, got {volume.ndim}D at {path}")
        raise ValueError(f"Expected 3D volume, but {path} is {volume.ndim}D.")

    logger.info(f"Successfully loaded volume with shape: {volume.shape}")
    return volume.astype(np.float32)


def save_nifti(volume: np.ndarray, reference_path: str | Path, output_path: str | Path) -> None:
    """
    Save 3D MRI volume of single object as a NIfTI file.

    :param volume: 3D numpy array representing the MRI volume.
    :param reference_path: Path to the reference scan.
    :param output_path: Path to the output NIfTI file.
    """
    output_path = Path(output_path)
    reference_path = Path(reference_path)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Could not create output directory {output_path.parent}: {e}")
        raise

    try:
        logger.debug(f"Loading reference metadata from: {reference_path}")
        reference_image = nib.load(str(reference_path))
        output_image = nib.Nifti1Image(
            volume,
            affine=reference_image.affine,
            header=reference_image.header
        )
        nib.save(output_image, str(output_path))
        logger.info(f"Successfully saved NIfTI to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to save NIfTI file to {output_path}: {e}")
        raise RuntimeError(f"Failed to save NIfTI file: {e}")
