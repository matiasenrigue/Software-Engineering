/**
 * Module: prediction.js
 * ----------------------
 * Contains functions to obtain ride predictions based on current/forecast weather
 * and station information.
 */

import { fetchForecastWeather } from "./weather.js";

window.combinedForecastAndPrediction = combinedForecastAndPrediction;

/**
 * Gets ride prediction by gathering the current timestamp,
 * weather data, and station information, then sends a POST request.
 */
export function getRidePrediction() {
  // Create a formatted timestamp.
  const now = new Date();
  const options = { weekday: "long", hour: "2-digit", minute: "2-digit" };

  // Retrieve weather data from the global variable (set in weather.js).
  const timestamp = window.TimestampWeather ? window.TimestampWeather : "N/A";
  console.log("Timestamp:", timestamp);
  const temperature = window.fullWeatherData ? window.fullWeatherData.temp : "N/A";
  const humidity = window.fullWeatherData ? window.fullWeatherData.humidity : "N/A";

  // Get destination station id from a global variable.
  const station_id = window.selectedStationId;
  if (!station_id) {
    alert("Please select a station first!");
    return;
  }
  const originStationId = window.originStationId;

  // Create the payload.
  const payload = {
    timestamp: timestamp,
    temperature: temperature,
    humidity: humidity,
    origin_station_id: originStationId,
    destination_station_id: station_id,
  };

  // Send the POST request to get the ride prediction.
  fetch("/api/ride_prediction", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => {
      // Update the UI with prediction results.
      console.log("Prediction data:", data);
      console.log("Prediction data:", data.prediction);
      document.getElementById("prediction-result-origin").innerHTML =
        "Prediction of Available Bikes at Origin: " + data.prediction.origin_station_id;
      document.getElementById("prediction-result-destination").innerHTML =
        "Prediction of Available Stands at Destination: " + data.prediction.destination_station_id;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

/**
 * Combines the forecast weather fetch and ride prediction.
 * Waits for forecast data before predicting.
 */
export async function combinedForecastAndPrediction() {
  await fetchForecastWeather();
  getRidePrediction();
}
