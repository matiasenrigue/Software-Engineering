/**
 * Module: maps.js
 * ----------------
 * Contains all functions for initializing the Google Map,
 * placing markers for bike stations, handling station selection,
 * drawing routes (arrows), and calculating distances/times.
 */

import { getLiveInfo } from "./prediction.js";
import { fetchBikesData } from './bikes.js';



// Global variables for map functionalities.
export let map; // The Google Map instance.
export let selectedStationId = null; // Currently selected station id.
export let stationMarkers = {}; // Dictionary holding markers by station id.
export let routePolyline = null; // Holds the drawn polyline arrow.

// Expose selectStation globally for inline event handlers.
window.selectStation = selectStation;
window.estimateArrivalTime = estimateArrivalTime;


/**
 * Initializes the Google Map.
 * Centers the map either on Dublin or on a user’s default station (if defined).
 */
export function initMap() {
  // Default center: Dublin.
  let centerCoordinates = { lat: 53.3498, lng: -6.2603 };
  // If defaultStation is defined in the global scope, re-center on it.
  if (typeof defaultStation !== "undefined" && defaultStation) {
    centerCoordinates = { lat: defaultStation.lat, lng: defaultStation.lng };
    window.defaultStation = defaultStation; // Expose for prediction.js.
  }
  map = new google.maps.Map(document.getElementById("map"), {
    center: centerCoordinates,
    zoom: 14,
    mapTypeId: google.maps.MapTypeId.SATELLITE,
  });
  // console.log(stations);

  fetchBikesData(); // now safe because the API is loaded

}


/**
 * Selects a station on the map.
 * Updates marker icons, draws a route arrow, calculates distance and time,
 * and updates the sidebar with details.
 * @param {number} stationId - Selected station id.
 * @param {string} stationName - Selected station name.
 * @param {number} stationLat - Latitude of the selected station.
 * @param {number} stationLng - Longitude of the selected station.
 */
export function selectStation(stationId, stationName, stationLat, stationLng) {
  // Reset icon for previously selected station.
  if (selectedStationId && stationMarkers[selectedStationId]) {
    stationMarkers[selectedStationId].setIcon("/static/pics/bike-yellow.png");
  }

  selectedStationId = stationId;
  window.selectedStationId = stationId; // Expose for prediction.js.
  
  window.dispatchEvent(new CustomEvent('stationSelected'));

  // Set new icon for selected station.
  if (stationMarkers[stationId]) {
    stationMarkers[stationId].setIcon("/static/pics/bike-green.png");
  }

  // Draw route arrow from the default station to the selected station.
  let from = { lat: defaultStation.lat, lng: defaultStation.lng };
  let to = { lat: stationLat, lng: stationLng };
  drawArrow(from, to, map);

  // Calculate distance between stations.
  const distance = calculateDistance(
    defaultStation.lat,
    defaultStation.lng,
    stationLat,
    stationLng
  );

  // Find selected station data.
  const selectedStation = stations.find((s) => s.station_id == stationId);
  const availableBikeStands = selectedStation ? selectedStation.available_bike_stands : 0;

  // Calculate cycling time.
  const cyclingMinutes = getCyclingTimeMinutes(distance);
  const cyclingTime = formatTime(cyclingMinutes);
  const arrivalTime = estimateArrivalTime(cyclingMinutes);

  
  // Check if element "selection-text" exists, then remove it.
    const selectionTextElem = document.getElementById("selection-text");
    if (selectionTextElem) {
      selectionTextElem.remove();
    }
  
    // Update sidebar details.
  document.getElementById("selected-location").textContent =
    `Destination: ${stationName}`;
  document.getElementById("selected-location-distance").textContent =
    `Distance: ${distance.toFixed(2)} km`;
  document.getElementById("selected-location-time").textContent =
    `Estimated Cycling Time: ${cyclingTime}`;
  window.cyclingTime = cyclingMinutes; // Expose for prediction.js.
  document.getElementById("selected-location-arrival").textContent =
    `Estimated Arrival Time: ${arrivalTime}h`;

  // Check which mode is active.
  const currentForecastType = document.querySelector('input[name="forecastType"]:checked').value;
  if (currentForecastType === "current") {
    // In ride now mode, automatically call live info to update the live info display.
    // (The live info will update automatically without a button.)
    getLiveInfo();
  } else if (currentForecastType === "forecast") {
    // In prediction mode, update the button text.
    const predictionBtn = document.getElementById("getRidePredictionBtn");
    if (window.selectedStationId) {
      predictionBtn.textContent = "Get Ride Prediction";
    }
  }


}


/**
 * Places markers on the map based on provided stations data.
 * @param {Array} stations_data - Array of station objects.
 */
export function placeMarkers(stations_data) {
  let oneWindowWasOpen = false;
  let currentInfoWindow;

  stations_data.forEach((station) => {
    // console.log(station);

    if (station.position && station.position.lat && station.position.lng) {
      // Set icon: default station gets a red bike, others get yellow.
      let iconUrl =
        station.station_id == defaultStation.id
          ? "/static/pics/bike-red.png"
          : "/static/pics/bike-yellow.png";

      // Create the marker.
      let marker = new google.maps.Marker({
        position: { lat: station.position.lat, lng: station.position.lng },
        map: map,
        title: station.name,
        icon: iconUrl,
      });

      // Store the marker for later updates.
      stationMarkers[station.station_id] = marker;

      // Build the content for the info window.
      let infoContent = `<h3>${station.name}</h3>
        <p>Total Bike Stands: ${station.bike_stands || 0}</p>
        <p>Available Bikes: ${station.available_bikes || 0}</p>
        <p>Available Stands: ${station.available_bike_stands || 0}</p>
        <a href="./station/${station.station_id}">
          <button>Details</button>
        </a>`;

      // Add a "GO" button for non-default stations.
      if (station.station_id != defaultStation.id) {
        infoContent += `<button onclick="selectStation(${station.station_id}, '${station.name}', ${station.position.lat}, ${station.position.lng})">Ride Prediction</button>`;
      }


      
      infoContent += '</div>'; // Close the wrapper div

      // Create the info window.
      let infoWindow = new google.maps.InfoWindow({
        content: infoContent,
        // Add custom InfoWindow styling options
        maxWidth: 250,
        pixelOffset: new google.maps.Size(0, 0),
      });

      // Add a click listener to open the info window.
      marker.addListener("click", () => {
        if (oneWindowWasOpen && currentInfoWindow) {
          currentInfoWindow.close();
        }
        oneWindowWasOpen = true;
        infoWindow.open(map, marker);
        currentInfoWindow = infoWindow;
      });
    }
  });
}





/**
 * Draws an arrow (polyline) between two points on the map.
 * @param {Object} from - Starting point {lat, lng}.
 * @param {Object} to - Ending point {lat, lng}.
 * @param {Object} mapInstance - The Google Map instance.
 */
export function drawArrow(from, to, mapInstance) {
  // Remove previous arrow, if any.
  if (routePolyline) {
    routePolyline.setMap(null);
  }

  // Define arrow symbol.
  const arrowSymbol = {
    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
    scale: 2,
    strokeColor: "#FF0000",
  };

  // Create a new polyline with the arrow.
  routePolyline = new google.maps.Polyline({
    path: [from, to],
    icons: [
      {
        icon: arrowSymbol,
        offset: "100%",
      },
    ],
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2,
    map: mapInstance,
  });
}


/**
 * Calculates the distance between two latitude/longitude points using the haversine formula.
 * @param {number} lat1 - Latitude of the first point.
 * @param {number} lon1 - Longitude of the first point.
 * @param {number} lat2 - Latitude of the second point.
 * @param {number} lon2 - Longitude of the second point.
 * @returns {number} Distance in kilometers.
 */
export function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in kilometers.
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    0.5 -
    Math.cos(dLat) / 2 +
    (Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      (1 - Math.cos(dLon))) /
      2;
  return R * 2 * Math.asin(Math.sqrt(a));
}



/**
 * Calculates cycling time (in minutes) for a given distance assuming an average speed.
 * @param {number} distance - Distance in kilometers.
 * @param {number} [avgSpeed=12] - Average cycling speed (km/h).
 * @returns {number} Cycling time in minutes.
 */
export function getCyclingTimeMinutes(distance, avgSpeed = 12) {
  return (distance / avgSpeed) * 60;
}


/**
 * Formats minutes into a human-readable string (e.g., "1 hr 20 min").
 * @param {number} minutes - Time in minutes.
 * @returns {string} Formatted time string.
 */
export function formatTime(minutes) {
  const hrs = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return hrs > 0 ? `${hrs} hr ${mins} min` : `${mins} min`;
}

/**
 * Estimates the arrival time by adding cycling minutes to the current time.
 * @param {number} cyclingMinutes - Cycling time in minutes.
 * @returns {string} Estimated arrival time (e.g., "3:45 PM").
 */
export function estimateArrivalTime(cyclingMinutes, departureTime = NaN) {

  console.log("departureTime:", departureTime);

  // If departureTime is not provided, use the current time.
  if (isNaN(departureTime)) {
    departureTime = Date.now();
  }

  console.log("Departure Time:", departureTime);
  console.log("Cycling Minutes:", cyclingMinutes);

  const arrival = new Date(departureTime + cyclingMinutes * 60000);
  console.log("Arrival Time:", arrival);
  
  return arrival.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}


document.querySelectorAll('.go-button').forEach(button => {
  button.addEventListener('click', (event) => {
    console.log("Ride Prediction button clicked:", event.target);
    const stationId = event.target.dataset.stationId;
    const stationName = event.target.dataset.stationName;
    const stationLat = parseFloat(event.target.dataset.stationLat);
    const stationLng = parseFloat(event.target.dataset.stationLng);
    selectStation(stationId, stationName, stationLat, stationLng);
  });
});



export function updateEstimatedArrivalTime() {
  const selectedForecast = document.querySelector('input[name="forecastType"]:checked').value;
  let departureTime;

  if (selectedForecast === "forecast") {
    // If Bike Later is selected, get the forecast date/time value.
    const forecastDateInput = document.getElementById("forecast-date");
    const forecastTimeInput = document.getElementById("forecast-hour");
    if (forecastDateInput && forecastDateInput.value) {
      let targetDatetime = forecastDateInput.value;
      if (forecastTimeInput && forecastTimeInput.value) {
        targetDatetime += "T" + forecastTimeInput.value;
      } else {
        targetDatetime += "T12:00:00"; // Default to noon if no time provided.
      }
      // Use the forecast timestamp as departure time.
      departureTime = Date.parse(targetDatetime);
    } else {
      // Fallback in case forecast date is not set.
      departureTime = Date.now();
    }
  } else {
    // For "Bike Now", use the current time.
    departureTime = Date.now();
  }
  
  // Make sure there's a valid cycling time value stored in window.cyclingTime.
  if (typeof window.cyclingTime === "number" && !isNaN(window.cyclingTime)) {
    const newArrivalTime = estimateArrivalTime(window.cyclingTime, departureTime);
    document.getElementById("selected-location-arrival").textContent =
      `Estimated Arrival Time: ${newArrivalTime}h`;
  } else {
    console.log("Cycling time is not defined properly.");
  }
}

// Expose initMap to the global scope for the Google Maps API callback.
window.initMap = initMap;

