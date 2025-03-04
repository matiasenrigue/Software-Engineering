let map;

function initMap() {

    let oneWindowWasOpen = false;

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
                        <p>Total Bike Stands: ${station.bike_stands || 'N/A'}</p>
                        <p>Available Bikes: ${station.available_bikes || 'N/A'}</p>
                        <p>Available Stands: ${station.available_bike_stands || 'N/A'}</p>
                        <a href="./station/${station.station_id}">
                        <button>Details</button>
                        </a>
                        `
                        // <!-- 'Details' button linking to the station details view -->
                        // <a href="{{ url_for('station_view', station_id=station.station_id) }}">
                        
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
