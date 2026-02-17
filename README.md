# 3D Egg Tray MRI Transformation Pipeline

This repository provides an automated 3D image processing pipeline for segmenting and extracting individual egg volumes from a 12-egg tray MRI scan.

The solution is implemented using a modular design covering preprocessing, segmentation, connected component extraction, and deterministic ID assignment. 
The pipeline supports structured transformation logic, unit testing using pytest, and containerized execution through Docker to ensure reproducibility and production-readiness.

---

## Project Structure

```

├── 3d_egg_pipeline.ipynb     Project report
├── config.yml                Configuration parameters and paths
├── data/                     Input MRI scans
├── scripts/                  Core transformation pipeline modules
│   ├── __init__.py
│   ├── labeling.py
│   ├── logger.py
│   ├── segmentation.py
│   ├── transformation_pipeline.py
│   └── utils.py
├── main.py                   Production entry point
├── tests/                    Pytest unit tests
│   ├── __init__.py
│   └── test_pipeline.py
├── docker-compose.yml        
├── Dockerfile
├── requirements.txt
├── setup.py
├── results/                  Output directory

```

---

## Running with Docker

### 1. Build the image

```

docker compose build

```

### 2. Run the pipeline

Processes the MRI scan located in `./data` and saves individual egg volumes to `./results`.

```

docker compose up mri-pipeline

```

### 3. Run unit tests

Executes the pytest suite to validate preprocessing, segmentation, labeling, and pipeline logic.

```

docker compose run --rm mri-tests

```

Tests can be executed at any time independently of the pipeline run.

---

## Local Development (Without Docker)

Create Virtual environment:

```

python -m venv venv
source venv/bin/activate

```

Install dependencies:

```

pip install -r requirements.txt
pip install -e .

```

Run the pipeline:

```

python main.py

```

Run tests locally:

```

pytest

```

---

---

## Testing

The repository uses `pytest` to verify:

- Intensity normalization and preprocessing
- Foreground segmentation
- Connected component extraction
- Deterministic ID assignment
- End-to-end pipeline behavior

Tests focus on validating logic independently of file system side effects.

---

## Notes

- The pipeline assumes a fixed 3×4 tray layout with deterministic row-major ID ordering.
- The Jupyter notebook (`3d_egg_pipeline.ipynb`) contains the technical report including assumptions, validation visuals, and scalability discussion.
---
