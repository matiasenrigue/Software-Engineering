/**
 * Initializes the switch button functionality for "Bike Now" and "Bike Later".
 * This attaches event listeners to radio buttons and the forecast date input so that
 * the forecast options and hour selector are shown or hidden appropriately.
 */

import { getLiveInfo, displayRidePrediction } from "./prediction.js";


export function initSwitchButton() {
  const radioButtons = document.querySelectorAll('input[name="forecastType"]');
  const forecastOptions = document.getElementById('forecast-options');
  const predictionBtn = document.getElementById("getRidePredictionBtn");
  const predictionElements = [
    document.getElementById('prediction-text'),
    document.getElementById('prediction-date'),
    document.getElementById('prediction-result-origin'),
    document.getElementById('prediction-result-destination')
  ];

  getLiveInfo();
  
  radioButtons.forEach((radio) => {
    radio.addEventListener('change', () => {
      if (radio.value === 'forecast') {
        // For prediction mode, show forecast options and the button.
        forecastOptions.classList.remove('forecast-options-hidden');
        predictionBtn.style.display = "inline-block";
        // If no station has been selected, do not change its text.
        if (!window.selectedStationId) {
          predictionBtn.textContent = "Select station";
        } else {
          predictionBtn.textContent = "Get Ride Prediction";
        }
        displayRidePrediction();

      } else {
        // For ride now mode, hide forecast options and the button.
        forecastOptions.classList.add('forecast-options-hidden');
        predictionBtn.style.display = "none";
        // Clear any previous prediction text.
        predictionElements.forEach((elem) => {
          if (elem) elem.innerHTML = '';
        });

        getLiveInfo();
      }
    });
  });
  
  // Also, attach event listeners to the forecast date input so the hour selector appears when needed.
  const forecastDate = document.getElementById('forecast-date');
  const hourSelector = document.getElementById('hour-selector');
  if (forecastDate && hourSelector) {
    forecastDate.addEventListener('change', () => {
      hourSelector.classList.remove('hour-selector-hidden');
    });
  }
}

document.addEventListener('DOMContentLoaded', initSwitchButton);


  