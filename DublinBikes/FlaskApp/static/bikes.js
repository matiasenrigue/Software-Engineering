// Global variable to track when the bikes data was last fetched
// let lastFetchTime = 0; 

// This function fetches updated bikes data from your API,
// updates the global stations variable, and then calls updateMarkers
function fetchBikesData() {

  // const now = Date.now();
  // if (now - lastFetchTime < 60000) {
  //   console.log("Using recently fetched bikes data.");
  //   return;
  // }

  fetch('/api/current_bikes')
    .then(response => response.json())
    .then(data => {
      lastFetchTime = Date.now();
      console.log("Fetched bikes data:", data);
      // Update global stations variable with the API data
      window.stations = data;
      // Call function to redraw markers with the new data
      updateMarkers(data);
    })
    .catch(error => {
      console.error("Error fetching bikes data:", error);
    });
}

// This function updates the markers on the map using new stations data.
// It removes old markers and calls the placeMarkers function (defined in maps.js).
function updateMarkers(stationsData) {
  // Remove old markers
  for (const id in stationMarkers) {
    stationMarkers[id].setMap(null);
  }
  // Reset the marker dictionary
  stationMarkers = {};
  console.log("Removed old markers.");
  console.log(stationMarkers);
  console.log("Placing new markers.");
  console.log(stationsData);

  // Call the existing function (in maps.js) to place markers
  placeMarkers(stationsData);
  
  // If a marker was previously selected, reopen its info window
  if (selectedStationId && stationMarkers[selectedStationId]) {
    google.maps.event.trigger(stationMarkers[selectedStationId], 'click');
  }
}

// Optionally, fetch on page load:
document.addEventListener("DOMContentLoaded", fetchBikesData);
