from flask import request, jsonify
import pickle
import numpy as np
import pandas as pd
import os


def prediction(data: dict, origin_station: dict, destination_station: dict):
    """
    Predict ride availability for both the origin and destination stations using station-specific ML models.

    This function loads pre-trained models (stored as pickle files) for each station and uses input data to predict:
      - The number of available bikes at the origin station.
      - The number of available bike stands at the destination station.
      
    The prediction is based on a feature vector computed from the input parameters. These features include:
      - Cyclical time features computed from the provided timestamp.
      - The current temperature and relative humidity.
      - One-hot encoded day-of-week features (with Monday as the baseline).
      
    For the origin station, the predicted value is adjusted to be within the range [0, total bike stands at origin].  
    For the destination station, the prediction is subtracted from the total bike stands at the destination, then
    clamped between 0 and the total bike stands at the destination.

    Args:
        data (dict): A dictionary containing input parameters with the following keys:
            - "timestamp" (str): A string representing the prediction time (e.g., "2025-04-02 14:30").
            - "temperature" (float): The current temperature.
            - "humidity" (float): The current relative humidity.
            - "origin_station_id" (int): The station ID for which to predict available bikes.
            - "destination_station_id" (int): The station ID for which to predict available stands.
        origin_station (dict): A dictionary with details of the origin station (must include "bike_stands").
        destination_station (dict): A dictionary with details of the destination station (must include "bike_stands").

    Returns:
        flask.Response: A JSON response with a dictionary containing the predictions. For example:
            {
                "prediction": {
                    "origin_station_id": <predicted_available_bikes>,
                    "destination_station_id": <predicted_available_stands>
                }
            }

    Raises:
        ValueError: If required input parameters are missing or invalid.
        Exception: If the station model cannot be loaded or if the prediction process fails.
    """
    
    print(f"Received data: {data}")
    bike_stands_origin = origin_station["bike_stands"]
    bike_stands_destination = destination_station["bike_stands"]

    # Extract data from request
    timestamp_str = data.get("timestamp")
    try:
        temperature = float(data.get("temperature"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing temperature"}), 400

    try:
        humidity = float(data.get("humidity"))  
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid humidity value"}), 400

    # Convert timestamp string to a datetime object
    try:
        dt = pd.to_datetime(timestamp_str)
    except Exception as e:
        print(f"Timestamp parsing error: {e}")
        return jsonify({"error": f"Timestamp parsing error: {e}"}), 400

    # Check that all arguments are present
    print(f"Received data: {data}")


    # Compute the features as used during training.
    time_of_day = (dt.hour * 60 + dt.minute) / (24 * 60)
    time_sin = np.sin(2 * np.pi * time_of_day)
    time_cos = np.cos(2 * np.pi * time_of_day)

    # Create one-hot encoded day-of-week features (drop Monday as baseline)
    # Monday = 0, Tuesday = 1, ... Sunday = 6.
    dow = dt.dayofweek  
    # We create six dummy features for Tuesday-Sunday.
    day_features = [0] * 6  
    if dow > 0:
        day_features[dow - 1] = 1

    # Construct the full feature vector.
    # The expected order: [time_sin, time_cos, temperature, humidity] + day-of-week dummies.
    features = [time_sin, time_cos, temperature, humidity] + day_features
    features = np.array(features).reshape(1, -1)
    
    predictions_dict = {}
    for station_predicted in ["origin_station_id", "destination_station_id"]:
        
        station_id = data.get(station_predicted)
        if station_id is None:
            return jsonify({"error": f"Missing {station_predicted}"}), 400

        # Define the path to the pickle file for this station.
        model_path = os.path.join(os.path.dirname(__file__), "pickle_models", f"model_station_{station_id}.pkl")
        
        # Get the number of Stands for the station.
        
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
        except Exception as e:
            print(f"Error loading model for station {station_id}: {e}")
            return jsonify({"error": f"Could not load model for station {station_id}: {e}"}), 500

        # Use the loaded model to predict the number of available bikes.
        try:
            prediction = model.predict(features)
            prediction_value = int(prediction[0])
            
            if station_predicted == "origin_station_id":
                # We predict bikes: So we are OKay with getting the number of bikes available
                prediction_value = max(0, prediction_value)
                prediction_value = min(prediction_value, bike_stands_origin)
            else:
                # We preidct the number of available bikes stands at the destination station.
                prediction_value = int(bike_stands_destination - prediction_value)
                prediction_value = max(0, prediction_value)
                prediction_value = min(prediction_value, bike_stands_destination)
            
            predictions_dict[station_predicted] = prediction_value
            
            print(f"Prediction: {prediction_value}")
        except Exception as e:
            print(f"Prediction error: {e}")
            return jsonify({"error": f"Prediction failed: {e}"}), 500

    # Return the prediction as JSON.
    print(f"Final prediction: {predictions_dict}")
    print(jsonify({"prediction": predictions_dict}))
    return jsonify({"prediction": predictions_dict})
