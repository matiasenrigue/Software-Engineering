document.addEventListener("DOMContentLoaded", function () {
  // Initially, fetch and display current weather
  fetchCurrentWeather();

  // Toggle between current and forecast selection
  const forecastRadios = document.getElementsByName("forecastType");
  forecastRadios.forEach((radio) => {
    radio.addEventListener("change", function () {
      const forecastOptions = document.getElementById("forecast-options");
      if (this.value === "forecast") {
        forecastOptions.style.display = "block";
      } else {
        forecastOptions.style.display = "none";
        // When user switches back to "Current", fetch current weather
        fetchCurrentWeather();
      }
    });
  });

  // When a date is selected, determine if hour selection should appear.
  document
    .getElementById("forecast-date")
    .addEventListener("change", function () {
      const selectedDate = new Date(this.value);
      const now = new Date();
      const diffDays = (selectedDate - now) / (1000 * 3600 * 24);
      const hourSelector = document.getElementById("hour-selector");
      if (diffDays < 1 || diffDays <= 4) {
        // If the chosen date is today or within 4 days, allow hour selection.
        hourSelector.style.display = "block";
      } else {
        hourSelector.style.display = "none";
      }
    });
});

/**
 * Parses an ISO timestamp and returns a formatted string with day and hour.
 * @param {string|number|Date} timestamp - The timestamp to format. Can be an ISO string, a Unix timestamp (milliseconds), or a Date object.
 * @returns {string} A formatted string, e.g., "Monday 02:30 PM".
 */
function formatTimestamp(timestamp) {
  // Create a Date object from the provided timestamp.
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);

  // Define options for day and time in 12-hour format.
  const options = {
    weekday: "long",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  };

  // Return the formatted date string using toLocaleString.
  return date.toLocaleString("en-US", options);
}

/**
 * Sets the weather icon <img> based on the icon code returned by OpenWeather.
 * @param {string} iconCode - For example "10d", "09n", etc.
 * @param {string} [elementId="weather-icon"] - The ID of the <img> element in the HTML.
 */
function setWeatherIcon(iconCode, elementId = "weather-icon") {
  if (!iconCode) return; // if missing, do nothing or show a placeholder

  // Build the relative path to your static/pics/weather_icons folder
  const iconUrl = `/static/pics/weather_icons/${iconCode}.png`;

  // Set the <img> src to the appropriate icon
  const imgElem = document.getElementById(elementId);
  if (imgElem) {
    imgElem.src = iconUrl;
  }
}

function fetchCurrentWeather() {
  // Your existing current weather fetch logic (or call an endpoint for current data)

  // Return the fetch promise so we can await it
  return fetch("/api/current_weather")
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Weather error:", data.error);
        return;
      }

      const rawTimestamp = data.timestamp_weatherinfo;
      document.getElementById("weather-current-forecast").textContent =
        "Current Weather:";
      document.getElementById("timestamp-weatherinfo").textContent =
        formatTimestamp(rawTimestamp);
      document.getElementById("weather-temp").textContent = data.temp + " °C";
      document.getElementById("weather-description").textContent =
        "Humidity: " + data.humidity + "%";

      setWeatherIcon(data.weather_id);

      // Add more updates as needed.
      window.fullWeatherData = data;
    })
    .catch((error) => {
      console.error("Error fetching weather data:", error);
    });
}

function fetchForecastWeather() {
  const selectedDate = document.getElementById("forecast-date").value;
  if (!selectedDate) {
    alert("Please select a valid date.");
    return;
  }

  // Build target datetime from the selected date and time.
  let targetDatetime = selectedDate; // ISO date (YYYY-MM-DD)
  const selectedTime = document.getElementById("forecast-hour").value;
  if (selectedTime) {
    targetDatetime += "T" + selectedTime;
  } else {
    // Default to noon if no hour is selected.
    targetDatetime += "T12:00:00";
  }

  // Forecast type is always hourly.
  const forecast_type = "hourly";
  const url = `/api/forecast_weather?forecast_type=${forecast_type}&target_datetime=${encodeURIComponent(targetDatetime)}`;

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error("Forecast error:", data.error);
        return;
      }

      // Update the weather info with data from the hourly forecast.
      document.getElementById("weather-current-forecast").textContent =
        "Forecast Weather for:";
      document.getElementById("timestamp-weatherinfo").textContent =
        formatTimestamp(data.timestamp_weatherinfo);
      document.getElementById("weather-temp").textContent = data.temp + " °C";
      document.getElementById("weather-description").textContent =
        "Humidity: " + data.humidity + "%";

      setWeatherIcon(data.weather_id);

      window.fullWeatherData = data;
    })
    .catch((error) => {
      console.error("Error fetching forecast data:", error);
    });
}
