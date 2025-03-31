/**
 * Module: bikes.js
 * -----------------
 * Contains functions for fetching current bikes data from the API
 * and updating map markers accordingly.
 */

import { placeMarkers, stationMarkers } from "./maps.js";

let lastFetchTime = 0;

/**
 * Waits until the Google Maps API is available before calling the callback.
 * @param {Function} callback - Function to call once google is defined.
 * @param {number} [retries=10] - Number of times to retry before giving up.
 */
function waitForGoogleMaps(callback, retries = 10) {
  if (typeof google !== "undefined") {
    callback();
  } else if (retries > 0) {
    setTimeout(() => waitForGoogleMaps(callback, retries - 1), 500);
  } else {
    console.error("Google Maps API not loaded after waiting.");
  }
}

/**
 * Fetches the current bikes data from the API.
 * Updates the global stations variable and calls updateMarkers.
 */
export function fetchBikesData() {
  fetch("/api/current_bikes")
    .then((response) => response.json())
    .then((data) => {
      lastFetchTime = Date.now();
      // Update global stations variable.
      window.stations = data;
      // Wait for the Google Maps API to load before updating markers.
      waitForGoogleMaps(() => updateMarkers(data));
    })
    .catch((error) => {
      console.error("Error fetching bikes data:", error);
    });
}


/**
 * Updates the map markers:
 * - Removes old markers.
 * - Calls placeMarkers to add new markers.
 * - If a station was previously selected, reopens its info window.
 * @param {Array} stationsData - Array of stations data.
 */
export function updateMarkers(stationsData) {
  // Remove old markers.
  for (const id in stationMarkers) {
    stationMarkers[id].setMap(null);
  }
  // Clear the stationMarkers object.
  for (const key in stationMarkers) {
    delete stationMarkers[key];
  }
  // console.log("Removed old markers.");
  // console.log(stationMarkers);
  // console.log("Placing new markers.");
  // console.log(stationsData);

  // Place new markers using the maps module function.
  placeMarkers(stationsData);

  // Reopen info window for previously selected station if it exists.
  if (window.selectedStationId && stationMarkers[window.selectedStationId]) {
    google.maps.event.trigger(stationMarkers[window.selectedStationId], "click");
  }
}

// Optionally, fetch bikes data on page load.
document.addEventListener("DOMContentLoaded", fetchBikesData);
