let map; // global map variable

// window.originStationId = default_station.id; // Set the default station id globally 

// Global variable to hold the currently selected station id.
let selectedStationId = null;

// Global dictionary to store markers by station id.
let stationMarkers = {};

// This function will be called when a user clicks the "GO" button.
function selectStation(stationId, stationName, stationLat, stationLng) {


// Reset the previously selected station's icon to black bike
if (selectedStationId && stationMarkers[selectedStationId]) {
  stationMarkers[selectedStationId].setIcon("/static/pics/bike-yellowpng");
}

  // Update the selected station ID.
  selectedStationId = stationId;
  window.selectedStationId = stationId; // Store in a global variable for prediction.js

// For the newly selected station, use green bike
if (stationMarkers[stationId]) {
  stationMarkers[stationId].setIcon("/static/pics/bike-green.png");
}

  

  
  // Draw the arrow from the default station to the selected station.
  // Assume defaultStation has properties lat and lng.
  let from = { lat: defaultStation.lat, lng: defaultStation.lng };
  let to = { lat: stationLat, lng: stationLng };
  drawArrow(from, to, map);  // Note: map variable must be in scope


  // Calculate the distance between the default and selected station.
  const distance = calculateDistance(defaultStation.lat, defaultStation.lng, stationLat, stationLng);

  // Find the selected station data (assuming the global "stations" variable is available)
  const selectedStation = stations.find(s => s.station_id == stationId);
  const availableBikeStands = selectedStation ? selectedStation.available_bike_stands : "N/A";

  // Estimate cycling time in minutes and then format it.
  const cyclingMinutes = getCyclingTimeMinutes(distance);
  const cyclingTime = formatTime(cyclingMinutes);

  // Estimate arrival time based on current time.
  const arrivalTime = estimateArrivalTime(cyclingMinutes);
  
  // Update the sidebar text to show the station name and distance.
  document.getElementById("selected-location").textContent = `Displaying directions to station: ${stationName}`;
  document.getElementById("selected-location-distance").textContent = `Distance: ${distance.toFixed(2)} km`;
  document.getElementById("selected-location-time").textContent = `Estimated Cycling Time: ${cyclingTime}`;
  document.getElementById("selected-location-arrival").textContent = `Estimated Arrival Time: ${arrivalTime}`;
  document.getElementById("selected-station-info").textContent = `Available Bike Stands: ${availableBikeStands}`;

}



function initMap() {

  // Set initial map center (Dublin)
  let centerCoordinates = { lat: 53.3498, lng: -6.2603 };

  // If defaultStation is defined, re-center on that station.
  if (typeof defaultStation !== 'undefined' && defaultStation) {
    centerCoordinates = { lat: defaultStation.lat, lng: defaultStation.lng };
  }

  // Initialize the map.
  map = new google.maps.Map(document.getElementById("map"), {
    center: centerCoordinates,
    zoom: 14,
    mapTypeId: google.maps.MapTypeId.SATELLITE
  });

  // Place the markers with the SQL Data to have ALL the stations ready on the map.
  // placeMarkers(stations)
  console.log(stations);

}



// Function to plavce markers on the map
function placeMarkers(stations_data) {

  let oneWindowWasOpen = false;
  let currentInfoWindow;


// Loop through the stations data passed from the template.
  stations_data.forEach(station => {
    console.log(station);

    if (station.position && station.position.lat && station.position.lng) {
      
      // Set the icon
      let iconUrl = (station.station_id == defaultStation.id)
      ? "/static/pics/bike-red.png"    // Default station = red bike
      : "/static/pics/bike-yellow.png"; // Others = black bike

      // Create the marker.
      let marker = new google.maps.Marker({
        position: { lat: station.position.lat, lng: station.position.lng },
        map: map,
        title: station.name,
        icon: iconUrl
      });

      // Save the marker in our global dictionary.
      stationMarkers[station.station_id] = marker;

      // Build the content for the info window.
      let infoContent = `<h3>${station.name}</h3>
        <p>Total Bike Stands: ${station.bike_stands || 'N/A'}</p>
        <p>Available Bikes: ${station.available_bikes || 'N/A'}</p>
        <p>Available Stands: ${station.available_bike_stands || 'N/A'}</p>
        <a href="./station/${station.station_id}">
          <button>Details</button>
        </a>`;

      // Only add the "GO" button if this is not the default station.
      if (station.station_id != defaultStation.id) {
        // infoContent += `<button onclick="selectStation(${station.station_id}, '${station.name}')">GO</button>`;
        infoContent += `<button onclick="selectStation(${station.station_id}, '${station.name}', ${station.position.lat}, ${station.position.lng})">GO</button>`;

      }

      // Create the info window.
      let infoWindow = new google.maps.InfoWindow({
        content: infoContent
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


// Global variable to hold the polyline arrow
let routePolyline = null;

// Function to draw a polyline with an arrow between two points
function drawArrow(from, to, map) {
  // Remove the previous arrow, if any.
  if (routePolyline) {
    routePolyline.setMap(null);
  }

  // Define an arrow symbol
  const arrowSymbol = {
    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
    scale: 2,
    strokeColor: '#FF0000'
  };

  // Create a polyline connecting the two coordinates
  routePolyline = new google.maps.Polyline({
    path: [from, to],
    icons: [{
      icon: arrowSymbol,
      offset: '100%' // display arrow at the end of the line
    }],
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2,
    map: map
  });
}


function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
      0.5 - Math.cos(dLat)/2 + 
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      (1 - Math.cos(dLon))/2;
  return R * 2 * Math.asin(Math.sqrt(a));
}



/**
 * Calculates the cycling time (in minutes) for a given distance,
 * assuming an average cycling speed (default is 12 km/h).
 * @param {number} distance - Distance in kilometers.
 * @param {number} [avgSpeed=12] - Average cycling speed (km/h).
 * @returns {number} Time in minutes.
 */
function getCyclingTimeMinutes(distance, avgSpeed = 12) {
  return (distance / avgSpeed) * 60;
}

/**
 * Formats a number of minutes as a string like "1 hr 20 min" or "25 min".
 * @param {number} minutes - Total minutes.
 * @returns {string} Formatted time string.
 */
function formatTime(minutes) {
  const hrs = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return hrs > 0 ? `${hrs} hr ${mins} min` : `${mins} min`;
}

/**
 * Estimates the arrival time by adding the cycling minutes to the current time.
 * @param {number} cyclingMinutes - The cycling time in minutes.
 * @returns {string} The estimated arrival time (e.g., "3:45 PM").
 */
function estimateArrivalTime(cyclingMinutes) {
  const arrival = new Date(Date.now() + cyclingMinutes * 60000);
  return arrival.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
}




