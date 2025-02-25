let map;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 53.3498, lng: -6.2603 }, // Center the map on Dublin
        zoom: 14,
    });

    // Use the stations data passed from the template
    stations.forEach(station => {
        // Ensure the station has a valid position object
        if (station.position && station.position.lat && station.position.lng) {
            let marker = new google.maps.Marker({
                position: { lat: station.position.lat, lng: station.position.lng },
                map: map,
                title: station.name
            });

            let infoWindow = new google.maps.InfoWindow({
                content: `<h3>${station.name}</h3>
                          <p>Available Bikes: ${station.available_bikes || 'N/A'}</p>
                          <p>Available Stands: ${station.bike_stands}</p>`
            });

            marker.addListener("click", () => {
                infoWindow.open(map, marker);
            });
        }
    });
}
