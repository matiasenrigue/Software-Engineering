/**
 * Module: prediction.js
 * ----------------------
 * Contains functions to obtain ride predictions based on current/forecast weather
 * and station information.
 */

import { fetchForecastWeather } from "./weather.js";
import { estimateArrivalTime } from "./maps.js";
import { formatTimestamp } from "./weather.js";

window.combinedForecastAndPrediction = combinedForecastAndPrediction;

/**
 * Gets ride prediction by gathering the current timestamp,
 * weather data, and station information, then sends a POST request.
 */
export function getRidePrediction() {
  // Create a formatted timestamp.
  const now = new Date();

  // Retrieve weather data from the global variable (set in weather.js).
  const timestamp = window.TimestampWeather ? window.TimestampWeather : now.toISOString();
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
  
      document.getElementById("prediction-text").innerHTML =
        "Prediction Availability for: ";
      
      try{
        const formattedDate = formatTimestamp(timestamp);
        if (formattedDate === "Invalid Date") {
          // Fall back to current time if the formatted timestamp is invalid
          const currentDate = new Date();
          document.getElementById("prediction-date").innerHTML = currentDate.toLocaleString('en-US', {
            weekday: 'long',
            hour: '2-digit',
            minute: '2-digit'
          });
        } else {
          // Use the formatted timestamp if it's valid
          document.getElementById("prediction-date").innerHTML = formattedDate;
        }
      } catch (e) {
        // Handle any errors in the formatting process
        const currentDate = new Date();
        document.getElementById("prediction-date").innerHTML = currentDate.toLocaleString('en-US', {
          weekday: 'long',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
     
         
      document.getElementById("prediction-result-origin").innerHTML =
        "Bikes at Origin: " + data.prediction.origin_station_id;
      document.getElementById("prediction-result-destination").innerHTML =
        "Stands at Destination: " + data.prediction.destination_station_id;

      const departureTime = window.TimestampWeather && !isNaN(Date.parse(window.TimestampWeather))
      ? Date.parse(window.TimestampWeather)
      : Date.now();
      
      const arrivalTimePrediction = estimateArrivalTime(window.cyclingTime, departureTime);
      document.getElementById("selected-location-arrival").textContent =
        `Estimated Arrival Time: ${arrivalTimePrediction}h`;
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
  
  // Make sure the user has selected a station.
  const station_id = window.selectedStationId;
  if (!station_id) {
    alert("Please select a station first!");
    return;
  }
  
  // Check which forecast type is selected
  const forecastType = document.querySelector('input[name="forecastType"]:checked').value;
  
  
  if (forecastType === "forecast") {
    // For "Bike Later" option
    await fetchForecastWeather();
  }

  // Always get the ride prediction
  getRidePrediction();
}
