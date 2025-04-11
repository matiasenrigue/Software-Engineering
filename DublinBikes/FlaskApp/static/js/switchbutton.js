/**
 * Initializes the switch button functionality for "Bike Now" and "Bike Later".
 * This attaches event listeners to radio buttons and the forecast date input so that
 * the forecast options and hour selector are shown or hidden appropriately.
 */
export function initSwitchButton() {
    // Get all radio buttons with the name "forecastType"
    const radioButtons = document.querySelectorAll('input[name="forecastType"]');
    // Get the container that holds additional forecast options.
    const forecastOptions = document.getElementById('forecast-options');
  
    // Elements to clear when switching modes
    const predictionElements = [
      document.getElementById('prediction-text'),
      document.getElementById('prediction-date'),
      document.getElementById('prediction-result-origin'),
      document.getElementById('prediction-result-destination')
    ];
  
    // Attach change event listeners to each radio button
    radioButtons.forEach((radio) => {
      radio.addEventListener('change', () => {
        // If "Bike Later" is selected, display forecast options; else hide them.
        if (radio.value === 'forecast') {
          forecastOptions.classList.remove('forecast-options-hidden');
        } else {
          forecastOptions.classList.add('forecast-options-hidden');
        }
        // Clear previous prediction results.
        predictionElements.forEach((elem) => {
          if (elem) elem.innerHTML = '';
        });
      });
    });
  
    // Attach change event listener to forecast date input to show the hour selector.
    const forecastDate = document.getElementById('forecast-date');
    const hourSelector = document.getElementById('hour-selector');
    if (forecastDate && hourSelector) {
      forecastDate.addEventListener('change', () => {
        hourSelector.classList.remove('hour-selector-hidden');
      });
    }
  }
  
  // Automatically initialize when the DOM content has fully loaded.
  document.addEventListener('DOMContentLoaded', initSwitchButton);
  