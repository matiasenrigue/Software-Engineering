/**
 * Module: weather.js
 * -------------------
 * Provides functions for fetching and displaying current and forecast weather data.
 * Also includes helper functions to format timestamps and set weather icons.
 */

/**
 * Formats a timestamp into a human-readable string.
 * @param {string|number|Date} timestamp - The timestamp to format.
 * @returns {string} Formatted timestamp (e.g., "Monday 02:30 PM").
 */


export function formatTimestamp(timestamp) {
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
  const options = {
    weekday: "long",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  };
  return date.toLocaleString("en-US", options);
}

/**
 * Sets the weather icon for the provided element based on the icon code.
 * @param {string} iconCode - Icon code (e.g., "10d", "09n").
 * @param {string} [elementId="weather-icon"] - The ID of the <img> element.
 */
export function setWeatherIcon(iconCode, elementId = "weather-icon") {
  if (!iconCode) return;
  const iconUrl = `/static/pics/weather_icons/${iconCode}.png`;
  const imgElem = document.getElementById(elementId);
  if (imgElem) {
    imgElem.src = iconUrl;
  }
}

/**
 * Fetches the current weather data from the API and updates the UI.
 * Also stores the full data in window.fullWeatherData.
 */
export function fetchCurrentWeather() {
  return fetch("/api/current_weather")
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Weather error:", data.error);
        return;
      }
      const rawTimestamp = data.timestamp_weatherinfo;
      document.getElementById("weather-current-forecast").textContent = "Current Weather:";
      document.getElementById("timestamp-weatherinfo").textContent = formatTimestamp(rawTimestamp);
      document.getElementById("weather-temp").textContent = data.temp + " °C";
      document.getElementById("weather-description").textContent = "Humidity: " + data.humidity + "%";
      setWeatherIcon(data.weather_id);
      // Store full weather data for other modules.
      window.fullWeatherData = data;
    })
    .catch((error) => {
      console.error("Error fetching weather data:", error);
    });
}

/**
 * Fetches forecast weather data based on user-selected date/time.
 * Updates the UI with the forecast data and stores it in window.fullWeatherData.
 */
export function fetchForecastWeather() {
  const selectedDate = document.getElementById("forecast-date").value;
  if (!selectedDate) {
    alert("Please select a valid date.");
    return;
  }
  // Build target datetime string.
  let targetDatetime = selectedDate;
  const selectedTime = document.getElementById("forecast-hour").value;
  if (selectedTime) {
    targetDatetime += "T" + selectedTime;
  } else {
    targetDatetime += "T12:00:00"; // Default to noon.
  }
  const forecast_type = "hourly";
  const url = `/api/forecast_weather?forecast_type=${forecast_type}&target_datetime=${encodeURIComponent(targetDatetime)}`;
  window.TimestampWeather = targetDatetime;
  console.log("Fetching forecast weather for:", targetDatetime);

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Forecast error:", data.error);
        return;
      }
      document.getElementById("weather-current-forecast").textContent = "Forecast Weather for:";
      document.getElementById("timestamp-weatherinfo").textContent = formatTimestamp(data.timestamp_weatherinfo);
      document.getElementById("weather-temp").textContent = data.temp + " °C";
      document.getElementById("weather-description").textContent = "Humidity: " + data.humidity + "%";
      setWeatherIcon(data.weather_id);
      window.fullWeatherData = data;


    })
    .catch((error) => {
      console.error("Error fetching forecast data:", error);
    });
}


// Set up event listeners for weather controls after DOM is loaded.
document.addEventListener("DOMContentLoaded", function () {
  // Fetch current weather on load.
  fetchCurrentWeather();

  // Toggle between current and forecast weather views.
  const forecastRadios = document.getElementsByName("forecastType");
  forecastRadios.forEach((radio) => {
    radio.addEventListener("change", function () {
      const forecastOptions = document.getElementById("forecast-options");
      if (this.value === "forecast") {
        forecastOptions.style.display = "block";
      } else {
        forecastOptions.style.display = "none";
        fetchCurrentWeather();
      }
    });
  });

  // Show or hide the hour selector based on chosen date.
  document.getElementById("forecast-date").addEventListener("change", function () {
    const selectedDate = new Date(this.value);
    const now = new Date();
    const diffDays = (selectedDate - now) / (1000 * 3600 * 24);
    const hourSelector = document.getElementById("hour-selector");
    if (diffDays < 1 || diffDays <= 4) {
      hourSelector.style.display = "block";
    } else {
      hourSelector.style.display = "none";
    }
  });
});
