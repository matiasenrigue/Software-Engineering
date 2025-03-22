let map; // global map variable


// Global variable to hold the currently selected station id.
let selectedStationId = null;
// Global dictionary to store markers by station id.
let stationMarkers = {};

// This function will be called when a user clicks the "GO" button.
function selectStation(stationId, stationName, stationLat, stationLng) {
  // If a station was previously selected, reset its marker icon.
  if (selectedStationId && stationMarkers[selectedStationId]) {
    stationMarkers[selectedStationId].setIcon("http://maps.google.com/mapfiles/ms/icons/ltblue-dot.png");
  }
  
  // Update the selected station ID.
  selectedStationId = stationId;
  
  // Set the new marker's icon to a different color (green).
  if (stationMarkers[stationId]) {
    stationMarkers[stationId].setIcon("http://maps.google.com/mapfiles/ms/icons/green-dot.png");
  }
  
  // Draw the arrow from the default station to the selected station.
  // Assume defaultStation has properties lat and lng.
  let from = { lat: defaultStation.lat, lng: defaultStation.lng };
  let to = { lat: stationLat, lng: stationLng };
  drawArrow(from, to, map);  // Note: map variable must be in scope

  // Calculate the distance between the stations.
  const distance = calculateDistance(defaultStation.lat, defaultStation.lng, stationLat, stationLng);
  
  // Update the sidebar text to show the station name and distance.
  const locationText = document.getElementById("locationText");
  if (locationText) {
    locationText.textContent = `Displaying directions to station: ${stationName}`;
    locationText.textContent += ` (Distance: ${distance.toFixed(2)} km)`;
  }
}


function initMap() {
  let oneWindowWasOpen = false;
  let currentInfoWindow;

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
  });

  // Loop through the stations data passed from the template.
  stations.forEach(station => {
    if (station.position && station.position.lat && station.position.lng) {
      
      // Set the icon: default station in red, others in light blue.
      let iconUrl = (station.station_id == defaultStation.id) ?
        "http://maps.google.com/mapfiles/ms/icons/red-dot.png" : 
        "http://maps.google.com/mapfiles/ms/icons/ltblue-dot.png";

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

