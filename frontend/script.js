const API_BASE_URL = "http://localhost:5000/api"; 
let map;
let markers = [];

let searchTimer;

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    fetchRoasters();
    fetchCafes();

    // Search as you type for the global search
    const globalSearch = document.getElementById('global-search');
    if (globalSearch) {
        globalSearch.addEventListener('input', () => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                fetchCafes();
            }, 300); // Wait 300ms after last keystroke
        });
    }

    // Immediate search for dropdowns/filters
    ['roaster-filter', 'roast-filter'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => fetchCafes());
        }
    });

    const applyFilters = document.getElementById('apply-filters');
    if (applyFilters) {
        applyFilters.addEventListener('click', () => {
            fetchCafes();
        });
    }

    const clearFilters = document.getElementById('clear-filters');
    if (clearFilters) {
        clearFilters.addEventListener('click', () => {
            document.getElementById('global-search').value = '';
            document.getElementById('roaster-filter').value = '';
            document.getElementById('roast-filter').value = '';
            document.getElementById('origin-filter').value = '';
            fetchCafes();
        });
    }
});

function initMap() {
    map = L.map('map').setView([-23.5505, -46.6333], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

function fetchRoasters() {
    fetch(`${API_BASE_URL}/roasters`)
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('roaster-filter');
            if (!select) return;

            // Clear existing options except the first one (All Roasters)
            // Equivalent to select.find('option:not(:first)').remove();
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            data.forEach(roaster => {
                const option = document.createElement('option');
                option.value = roaster.id;
                option.textContent = roaster.name;
                select.appendChild(option);
            });
        })
        .catch(err => console.error("Error fetching roasters:", err));
}

function fetchCafes() {
    const query = document.getElementById('global-search').value;
    const roast = document.getElementById('roast-filter').value;
    const origin = document.getElementById('origin-filter').value;
    const roasterId = document.getElementById('roaster-filter').value;

    const resultsList = document.querySelector('.results-list');
    if (resultsList) {
        resultsList.innerHTML = '<div class="loading">Searching specialized inventory...</div>';
    }

    // BUILD QUERY PARAMS
    let params = [];
    if (query) params.push(`q=${encodeURIComponent(query)}`);
    if (roast) params.push(`roast=${roast}`);
    if (origin) params.push(`origin=${origin}`);
    if (roasterId) params.push(`roaster_id=${roasterId}`);
    
    const queryString = params.length > 0 ? `?${params.join('&')}` : '';

    fetch(`${API_BASE_URL}/cafes${queryString}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            renderResults(data);
            updateMarkers(data);
        })
        .catch(err => {
            if (resultsList) {
                resultsList.innerHTML = '<div class="error">Failed to load data. Is the backend running?</div>';
            }
            console.error("API Error:", err);
        });
}

function renderResults(cafes) {
    const countEl = document.getElementById('results-count');
    if (countEl) {
        countEl.textContent = `${cafes.length} found`;
    }

    const list = document.getElementById('results-list');
    if (!list) return;

    list.innerHTML = '';

    if (cafes.length === 0) {
        const noResults = document.createElement('div');
        noResults.className = 'no-results';
        noResults.textContent = 'No cafes found matching your filters.';
        list.appendChild(noResults);
        return;
    }

    cafes.forEach(cafe => {
        const beans = cafe.matching_beans || [];
        
        const beanTags = beans.map(b => `
            <div class="bean-tag">
                <strong>${b.name}</strong><br>
                <small>${b.roaster_name || 'Independent'} | ${b.roast_level} | ${b.origin}</small>
            </div>
        `).join('');
        
        const card = `
            <div class="cafe-card">
                <h3>${cafe.name}</h3>
                <div class="location">📍 ${cafe.location || 'Unknown Location'}</div>
                ${beans.length > 0 ? `<div class="inventory-header">Matching Beans:</div>` : ''}
                <div class="beans">
                    ${beanTags}
                </div>
            </div>
        `;
        list.insertAdjacentHTML('beforeend', card);
    });
}

function updateMarkers(cafes) {
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    cafes.forEach((cafe) => {
        const lat = -23.5505 + (Math.random() - 0.5) * 5;
        const lng = -46.6333 + (Math.random() - 0.5) * 5;
        const marker = L.marker([lat, lng]).addTo(map)
            .bindPopup(`<b>${cafe.name}</b><br>${cafe.location || ''}`);
        markers.push(marker);
    });

    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}
