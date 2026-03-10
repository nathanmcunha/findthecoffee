const API_BASE_URL = "http://localhost:5001/api";
let map;
let markers = [];

$(document).ready(function() {
    initMap();
    fetchCafes();

    $('#apply-filters').click(function() {
        fetchCafes();
    });

    $('#clear-filters').click(function() {
        $('#roast-filter').val('');
        $('#origin-filter').val('');
        fetchCafes();
    });
});

function initMap() {
    // Default to a central location (e.g., Seattle or SF)
    map = L.map('map').setView([47.6062, -122.3321], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

function fetchCafes() {
    const roast = $('#roast-filter').val();
    const origin = $('#origin-filter').val();

    let url = `${API_BASE_URL}/cafes?include=beans`;
    
    // Note: Our current backend API implementation for 'search' is only on /api/beans.
    // To implement real filtering on the 'Cafes with Beans' view, we have two options:
    // 1. Update the backend to support roast/origin filters on /api/cafes
    // 2. Filter the JSON locally (Client-side filtering)
    
    // For this prototype, let's do Client-Side Filtering to demonstrate the decoupled logic.
    
    $('.results-list').html('<div class="loading">Fetching the best beans...</div>');

    $.ajax({
        url: url,
        method: "GET",
        success: function(data) {
            let filteredData = data;

            if (roast || origin) {
                filteredData = data.filter(cafe => {
                    return cafe.beans.some(bean => {
                        const matchRoast = !roast || bean.roast_level === roast;
                        const matchOrigin = !origin || (bean.origin && bean.origin.toLowerCase().includes(origin.toLowerCase()));
                        return matchRoast && matchOrigin;
                    });
                });
            }

            renderResults(filteredData);
            updateMarkers(filteredData);
        },
        error: function(err) {
            $('.results-list').html('<div class="error">Failed to load data. Is the backend running?</div>');
            console.error("API Error:", err);
        }
    });
}

function renderResults(cafes) {
    $('#results-count').text(`${cafes.length} found`);
    const list = $('#results-list');
    list.empty();

    if (cafes.length === 0) {
        list.append('<div class="no-results">No cafes found matching your filters.</div>');
        return;
    }

    cafes.forEach(cafe => {
        const beanTags = cafe.beans.map(b => `<span class="bean-tag">${b.name} (${b.roast_level})</span>`).join('');
        
        const card = `
            <div class="cafe-card">
                <h3>${cafe.name}</h3>
                <div class="location">${cafe.location || 'Unknown Location'}</div>
                <div class="beans">
                    ${beanTags}
                </div>
            </div>
        `;
        list.append(card);
    });
}

function updateMarkers(cafes) {
    // Clear existing markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    // In a real app, cafes would have lat/lng. 
    // Since our schema doesn't have coordinates yet, we'll simulate them slightly
    // offset from the center so they don't overlap.
    
    cafes.forEach((cafe, index) => {
        const lat = 47.6062 + (Math.random() - 0.5) * 0.1;
        const lng = -122.3321 + (Math.random() - 0.5) * 0.1;
        
        const marker = L.marker([lat, lng]).addTo(map)
            .bindPopup(`<b>${cafe.name}</b><br>${cafe.location || ''}`);
        
        markers.push(marker);
    });

    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}
