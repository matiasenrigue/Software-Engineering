# Machine Learning Module

The **Machine Learning** folder is dedicated to building and deploying predictive models for the Dublin Bikes project. These models forecast bike availability and dock capacity at each station based on features such as time, weather, and historical usage patterns.

## Overview

This module includes:
- **Pre-trained Models:**  
  A collection of station-specific predictive models stored as pickle files. Each file (e.g., `model_station_1.pkl`, `model_station_2.pkl`, etc.) corresponds to a bike station.

- **Prediction Script:**  
  The `predict_availability.py` script contains the logic to load the appropriate model and generate predictions. This file is used by the Flask application to serve ride predictions via an API endpoint.

- **Training Notebooks:**  
  Two Jupyter notebooks are provided to support the model training process:
  - **training_part1_model_selection.ipynb:**  
    Contains experiments and analysis for selecting the best machine learning model based on the available data.
  - **training_part2_model_size_reduction.ipynb:**  
    Focuses on reducing model complexity and size while retaining predictive performance.

## Directory Structure

```
MachineLearning/
├── pickle_models
│   ├── model_station_1.pkl
│   ├── model_station_2.pkl
│   ├── ... 
│   └── model_station_99.pkl
├── predict_availability.py         # Script for loading models and predicting availability.
├── training_part1_model_selection.ipynb   # Notebook for model selection experiments.
└── training_part2_model_size_reduction.ipynb  # Notebook for model size reduction and refinement.
```

## Usage

- **Prediction:**  
  The `predict_availability.py` file is imported and called by the Flask API endpoint (e.g., `/api/ride_prediction`) to predict available bikes and stands for a given origin/destination pair. Ensure that the corresponding pickle files in the `pickle_models` folder are up to date.

- **Training:**  
  Open and run the training notebooks interactively to explore model performance, adjust features, or retrain models as new data becomes available.

---

For any modifications or further enhancements, please refer to the inline documentation within the scripts and notebooks.
