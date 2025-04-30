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
      
      document.getElementById("prediction-text").style.display = "block";
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
          document.getElementById("prediction-date").style.display = "block";
          window.predictionDate = formattedDate;
          document.getElementById("prediction-date").innerHTML = window.predictionDate;
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
     
      window.lastPredictionOrigin = data.prediction.origin_station_id;
      window.lastPredictionDestination = data.prediction.destination_station_id;
         
      document.getElementById("prediction-result-origin").innerHTML =
        "Bikes at Origin: " + window.lastPredictionOrigin;
      document.getElementById("prediction-result-destination").innerHTML =
        "Stands at Destination: " + window.lastPredictionDestination;

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


export function displayRidePrediction() {
  console.log("Displaying ride prediction...");
  document.getElementById("getRidePredictionBtn").style.display = "block";

   if (!window.lastPredictionOrigin || !window.lastPredictionDestination) {
    document.getElementById("prediction-result-origin").innerHTML = "Select a date to predict";
    document.getElementById("prediction-result-destination").innerHTML = "Select a date to predict";
    
      if (window.selectedStationId) {
      document.getElementById("selected-location-arrival").textContent = "Estimated Arrival Time: "   
      }

      return;
  }

  console.log("Displaying ride prediction...");
  document.getElementById("prediction-text").style.display = "block";
  document.getElementById("prediction-text").innerHTML = "Prediction Availability for: ";
  document.getElementById("prediction-date").style.display = "block";
  document.getElementById("prediction-date").innerHTML = window.predictionDate;
  
  document.getElementById("prediction-result-origin").innerHTML = "Bikes at Origin: " + window.lastPredictionOrigin;
  document.getElementById("prediction-result-destination").innerHTML = "Stands at Destination: " + window.lastPredictionDestination;

  document.getElementById("getRidePredictionBtn").style.display = "block";
}

/**
 * Gets live information from the selected station and updates the UI.
 */
export function getLiveInfo() {


  if (!window.stations) {
    return;
  }

  const destinationStationId = window.selectedStationId;
  const originStationId = window.defaultStation.id;



  if (!originStationId) {
    console.error("Origin station not found");
  }
  else {
    const originStation = window.stations.find(s => s.station_id == originStationId);
    document.getElementById("prediction-result-origin").innerHTML = "Bikes available: " + originStation.available_bikes;
  }

  if (!destinationStationId) {
    document.getElementById("prediction-result-destination").innerHTML = "Select a destination station";
  }
  else {
    const destinationStation = window.stations.find(s => s.station_id == destinationStationId);
    document.getElementById("prediction-result-destination").innerHTML = "Stands available: " + destinationStation.available_bike_stands;
    document.getElementById("getRidePredictionBtn").style.display = "none";
  }

    document.getElementById("prediction-text").style.display = "none";
    document.getElementById("prediction-date").style.display = "none";
    document.getElementById("getRidePredictionBtn").style.display = "none";
  


}

/**
 * Combines forecast weather and prediction or live info.
 * If Bike Later is selected, it fetches the forecast and then performs the prediction.
 * Otherwise (Bike Now), it simply displays live station info.
 */
export async function combinedForecastAndPrediction() {
  // Ensure a station has been selected.
  const station_id = window.selectedStationId;
  if (!station_id) {
    alert("Please select a station first!");
    return;
  }

  const forecastType = document.querySelector('input[name="forecastType"]:checked').value;
  if (forecastType === "forecast") {
    await fetchForecastWeather();
    getRidePrediction();
  }
  // For "Bike Now" mode, the button is hidden and live info is updated automatically.
}

