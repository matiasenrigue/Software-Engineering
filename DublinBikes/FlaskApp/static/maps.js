let map;


// Global variable to hold the currently selected station id.
let selectedStation = null;

// This function will be called when a user clicks the "GO" button.
function selectStation(stationId, stationName) {
  selectedStation = stationId;
  // Update the text element with the new message.
  const locationText = document.getElementById("locationText");
  if (locationText) {
    locationText.textContent = `Displaying directions to station: ${stationName}`;
  }
  // Optionally, you might also change the marker icon or add additional logic here.
}

function initMap() {

    let oneWindowWasOpen = false;

      // Set initial map center (Dublin)
    let centerCoordinates = { lat: 53.3498, lng: -6.2603 };

    // If defaultStation is defined, re-center on that station.
    if (typeof defaultStation !== 'undefined' && defaultStation) {
        centerCoordinates = { lat: defaultStation.lat, lng: defaultStation.lng };
    }

    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultStation,
        zoom: 14,
    });

    // Use the stations data passed from the template
    stations.forEach(station => {

        // Ensure the station has a valid position object
        if (station.position && station.position.lat && station.position.lng) {
            
            // Choose the icon based on whether this station is the default
            let iconUrl = (station.station_id == defaultStation.id) ?
            "http://maps.google.com/mapfiles/ms/icons/red-dot.png" : // Chosen station in red
            "http://maps.google.com/mapfiles/ms/icons/ltblue-dot.png"; // Other stations in a light color

            let marker = new google.maps.Marker({
                position: { lat: station.position.lat, lng: station.position.lng },
                map: map,
                title: station.name,
                icon: iconUrl
            });

            // Build the content for the info window.
            let infoContent = `<h3>${station.name}</h3>
            <p>Total Bike Stands: ${station.bike_stands || 'N/A'}</p>
            <p>Available Bikes: ${station.available_bikes || 'N/A'}</p>
            <p>Available Stands: ${station.available_bike_stands || 'N/A'}</p>
            <a href="./station/${station.station_id}">
            <button>Details</button>
            </a>
            `;
            
            // <!-- 'Details' button linking to the station details view -->
            // <a href="{{ url_for('station_view', station_id=station.station_id) }}">

            // Only add the "GO" button if this is not the default station.
            if (station.station_id != defaultStation.id) {
                infoContent += `<button onclick="selectStation(${station.station_id}, '${station.name}')">GO</button>`;
            }


            // Create the info window.
            let infoWindow = new google.maps.InfoWindow({
                content: infoContent
            });

            marker.addListener("click", () => {

                if (oneWindowWasOpen) {
                    currentInfoWindow.close();
                }

                oneWindowWasOpen = true;
                infoWindow.open(map, marker);
                currentInfoWindow = infoWindow;
            });
            
        }
    });
}
