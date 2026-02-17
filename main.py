"""
Main script for MRI transformation pipeline
"""

import yaml
from pathlib import Path
from scripts.utils import load_nifti, save_nifti
from scripts.transformation_pipeline import TransformationPipeline
from scripts.logger import setup_logger

def load_config(path: str = "config.yml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    # Load configuration
    config = load_config()

    paths = config["paths"]
    params = config["parameters"]
    logger = setup_logger(log_dir=paths["log_dir"])

    try:
        input_path = Path(paths["input_path"])
        output_dir = Path(paths["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Loading MRI volume")
        volume = load_nifti(input_path)

        # Initialize and run transformation pipeline
        pipeline = TransformationPipeline(
            sigma=params["sigma"],
            expected_egg_count=params["expected_egg_count"],
            row_tolerance=params["row_tolerance"],
        )

        results = pipeline.run(volume)

        logger.info("Saving extracted egg volumes")
        for egg_id, egg_volume in results.items():
            nii_path = output_dir / f"egg_{egg_id}.nii"

            save_nifti(
                egg_volume,
                reference_path=input_path,
                output_path=nii_path,
            )

        logger.info("Processing completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
