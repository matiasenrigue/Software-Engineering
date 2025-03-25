async function fetchWeather() {
    try {
      const response = await fetch('/api/weather');
      if (!response.ok) throw new Error('Failed to fetch weather');
  
      const data = await response.json();
      const weatherContainer = document.querySelector('.weather');
  
      // Clear previous weather classes
      weatherContainer.classList.remove('sunny', 'cloudy', 'rainy');
  
      // Set background class based on weather description
      const desc = data.description.toLowerCase();
      if (desc.includes('clear')) {
        weatherContainer.classList.add('sunny');
      } else if (desc.includes('cloud')) {
        weatherContainer.classList.add('cloudy');
      } else if (desc.includes('rain')) {
        weatherContainer.classList.add('rainy');
      }
  
      // Update weather content
      weatherContainer.innerHTML = `
        <h3>Live Weather</h3>
        <div class="weather-box">
          <img src="https://openweathermap.org/img/wn/${data.icon}@2x.png" alt="Weather Icon">
          <div class="weather-info">
            <p><strong>${data.temperature}°C</strong> - ${data.description}</p>
            <p><strong>Sunrise:</strong> ${data.sunrise}</p>
            <p><strong>Sunset:</strong> ${data.sunset}</p>
          </div>
        </div>
      `;
    } catch (error) {
      console.error('Weather error:', error);
      document.querySelector('.weather').innerHTML = `<p>Weather data unavailable.</p>`;
    }
  }
  
  document.addEventListener('DOMContentLoaded', fetchWeather);
  