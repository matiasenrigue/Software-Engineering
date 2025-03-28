function getRidePrediction() {

    // Create a timestamp formatted with day, hour and minute
    const now = new Date();
    const options = { weekday: 'long', hour: '2-digit', minute: '2-digit' };
    const timestamp = now.toLocaleString('en-US', options);
    
    // Retrieve weather data from a global variable if available (set by weather.js),
    // otherwise set default values.
    const temperature = window.fullWeatherData ? window.fullWeatherData.temp : "N/A";
    const rain = window.fullWeatherData && window.fullWeatherData.rain 
                 ? (window.fullWeatherData.rain["1h"] || 0)
                 : 0;
    const windspeed = window.fullWeatherData ? window.fullWeatherData.wind_speed : "N/A";
    
    // Get station ID from a global variable if set (e.g., when a station is selected), or default to 10.
    const station_id = window.selectedStationId
    if (!station_id) {
        alert("Please select a station first!");
        return;
    }

    const originStationId = window.originStationId
    
    
    // Create the payload to send
    const payload = {
        timestamp: timestamp,
        temperature: temperature,
        rain: rain,
        windspeed: windspeed,
        origin_station_id: originStationId,
        destination_station_id: station_id
    };

    // Send the POST request to the backend endpoint
    fetch('/api/ride_prediction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        // For now, simply show the prediction in an alert (or update the UI accordingly)
        document.getElementById("prediction-result-origin").innerHTML = "Prediction of Available Bikes at Origin: " + data.prediction;
        document.getElementById("prediction-result-destination").innerHTML = "Prediction of Available Bikes at Destination: " + (data.prediction + 5);
    })
    .catch(error => {
        console.error("Error:", error);
    });
}


async function combinedForecastAndPrediction() {
    await fetchForecastWeather();  // Wait until forecast is fetched and processed
    getRidePrediction();           // Then call the ride prediction function
  }
