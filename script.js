let map;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 53.3498, lng: -6.2603 }, // Dublin
        zoom: 14,
    });

    fetch("/api/stations")
        .then(response => response.json())
        .then(data => {
            data.forEach(station => {
                let marker = new google.maps.Marker({
                    position: { lat: station.position.lat, lng: station.position.lng },
                    map: map,
                    title: station.name
                });

                let infoWindow = new google.maps.InfoWindow({
                    content: `<h3>${station.name}</h3>
                              <p>Available Bikes: ${station.available_bikes}</p>
                              <p>Available Stands: ${station.available_bike_stands}</p>`
                });

                marker.addListener("click", () => {
                    infoWindow.open(map, marker);
                });
            });
        })
        .catch(error => console.error("Error fetching station data:", error));
}
