// Javascript for Leaflet Map on Strike Page

console.log("strikes.js loaded");

var strike_map = document.getElementById('strike_map');

var map = L.map(strike_map).setView([3.080829044238991, -72.64697923793776], 13);

// If the database does not contain lat and lon,
// use default coordinates in between Caribbean and Eastern Pacific
// Strike areas to show a general map on the strike page and don't show the circle

let lat, lon, zoom_level;

if(strike_map.getAttribute("data-lat") === null || strike_map.getAttribute("data-lon") === null){
    zoom_level = 4;
}else{
    lat = parseFloat(strike_map.dataset.lat);
    lon = parseFloat(strike_map.dataset.lon);
    zoom_level = 5;
    map.setView([lat, lon], 13);

    var circle = L.circle([lat, lon], {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.1,
    radius: 300000
    }).addTo(map);
}

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: zoom_level,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

