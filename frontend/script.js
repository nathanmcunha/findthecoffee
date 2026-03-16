// Initialize Lucide icons
lucide.createIcons();

const API_BASE_URL = "http://localhost:5000/api";
let map;
let markers = [];
let searchTimer;
let mapIsVisible = false;

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  fetchRoasters();
  fetchCafes();

  // Search and Filter Events
  const globalSearch = document.getElementById("global-search");
  if (globalSearch) {
    globalSearch.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        fetchCafes();
      }, 300); // 300ms Debounce
    });
  }

  // Immediate filters
  ["roaster-filter", "roast-filter"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", () => fetchCafes());
    }
  });

  // Text filters with debounce (Origin and CEP)
  ["origin-filter", "cep-filter"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
          fetchCafes();
        }, 400);
      });
    }
  });

  // Near Me Button (Geolocation)
  const nearMeBtn = document.getElementById("near-me-btn");
  if (nearMeBtn) {
    nearMeBtn.addEventListener("click", () => getUserLocation());
  }

  // Clear Filters
  const clearFilters = document.getElementById("clear-filters");
  if (clearFilters) {
    clearFilters.addEventListener("click", () => {
      document.getElementById("global-search").value = "";
      document.getElementById("roaster-filter").value = "";
      document.getElementById("roast-filter").value = "";
      document.getElementById("origin-filter").value = "";
      document.getElementById("cep-filter").value = "";
      fetchCafes();
    });
  }

  // Map Toggle
  const mapToggleBtn = document.getElementById("toggle-map-btn");
  const mapContainer = document.getElementById("map-container");
  const mapBtnText = document.getElementById("map-btn-text");

  mapToggleBtn.addEventListener("click", () => {
    mapIsVisible = !mapIsVisible;
    if (mapIsVisible) {
      mapContainer.classList.add("open");
      mapBtnText.textContent = "Ocultar Mapa";
      mapToggleBtn.classList.add("bg-brand-50", "text-brand-600");
      mapToggleBtn.classList.remove("bg-gray-50", "text-gray-600");
      // Invalidate Leaflet size to render correctly after opening the div
      setTimeout(() => {
        map.invalidateSize();
        // Recalculate bounds when opening the map to ensure markers appear
        if (markers.length > 0) {
          const group = new L.featureGroup(markers);
          map.fitBounds(group.getBounds().pad(0.1));
        }
      }, 300);
    } else {
      mapContainer.classList.remove("open");
      mapBtnText.textContent = "Ver Mapa";
      mapToggleBtn.classList.remove("bg-brand-50", "text-brand-600");
      mapToggleBtn.classList.add("bg-gray-50", "text-gray-600");
    }
  });
});

function initMap() {
  map = L.map("map").setView([-23.5505, -46.6333], 5);
  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      r: window.devicePixelRatio > 1 ? "@2x" : "",
    },
  ).addTo(map);
}

function fetchRoasters() {
  fetch(`${API_BASE_URL}/roasters`)
    .then((response) => response.json())
    .then((data) => {
      const select = document.getElementById("roaster-filter");
      if (!select) return;

      while (select.options.length > 1) {
        select.remove(1);
      }

      data.forEach((roaster) => {
        const option = document.createElement("option");
        option.value = roaster.id;
        option.textContent = roaster.name;
        select.appendChild(option);
      });
    })
    .catch((err) => console.error("Erro ao buscar torrefações:", err));
}

function fetchCafes() {
  const query = document.getElementById("global-search").value;
  const roast = document.getElementById("roast-filter").value;
  const roasterId = document.getElementById("roaster-filter").value;

  const resultsList = document.getElementById("results-list");

  // Loading state
  resultsList.innerHTML = `
                <div class="col-span-full flex justify-center py-12">
                    <div class="animate-pulse flex flex-col items-center">
                        <i data-lucide="loader-2" class="w-8 h-8 text-brand-500 animate-spin mb-4"></i>
                        <p class="text-gray-500 font-medium">Buscando o melhor café para você...</p>
                    </div>
                </div>
            `;
  lucide.createIcons(); // Recreate inserted icons

  // Build Query Params
  let params = [];

  // Combine global search and CEP if both exist
  let finalQuery = query;

  if (finalQuery) params.push(`q=${encodeURIComponent(finalQuery)}`);
  if (roast) params.push(`roast=${roast}`);
  if (roasterId) params.push(`roaster_id=${roasterId}`);

  const queryString = params.length > 0 ? `?${params.join("&")}` : "";

  fetch(`${API_BASE_URL}/cafes${queryString}`)
    .then((response) => {
      if (!response.ok) throw new Error("Falha na resposta da rede");
      return response.json();
    })
    .then((data) => {
      renderResults(data);
      updateMarkers(data);
    })
    .catch((err) => {
      resultsList.innerHTML = `
                        <div class="col-span-full py-12 text-center bg-red-50 rounded-2xl border border-red-100">
                            <i data-lucide="alert-circle" class="w-10 h-10 text-red-400 mx-auto mb-3"></i>
                            <h3 class="text-lg font-medium text-red-800">Erro ao carregar dados</h3>
                            <p class="text-red-600 mt-1">O servidor backend está rodando?</p>
                        </div>
                    `;
      lucide.createIcons();
      console.error("Erro na API:", err);
    });
}

function renderResults(cafes) {
  const countEl = document.getElementById("results-count");
  if (countEl) {
    countEl.textContent = `${cafes.length} ${cafes.length === 1 ? "encontrado" : "encontrados"}`;
  }

  const list = document.getElementById("results-list");
  if (!list) return;

  list.innerHTML = "";

  if (cafes.length === 0) {
    list.innerHTML = `
                    <div class="col-span-full py-16 text-center">
                        <div class="bg-gray-50 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                            <i data-lucide="coffee" class="w-10 h-10 text-gray-400"></i>
                        </div>
                        <h3 class="text-xl font-medium text-gray-900 mb-2">Nenhum café encontrado</h3>
                        <p class="text-gray-500">Tente ajustar seus filtros ou termo de busca.</p>
                    </div>
                `;
    lucide.createIcons();
    return;
  }

  cafes.forEach((cafe) => {
    const beans = cafe.matching_beans || [];

    // Map beans to stylized tags
    const beanTags = beans
      .map(
        (b) => `
                    <div class="bg-gray-50 rounded-xl p-3 border border-gray-100 mb-2 hover:bg-white hover:border-brand-200 hover:shadow-sm transition-all">
                        <div class="flex items-start justify-between">
                            <div>
                                <p class="font-semibold text-gray-900 text-sm">${b.name}</p>
                                <p class="text-xs text-gray-500 flex items-center gap-1 mt-1">
                                    <i data-lucide="building-2" class="w-3 h-3"></i> 
                                    ${b.roaster_name || "Independente"}
                                </p>
                            </div>
                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-brand-50 text-brand-700 border border-brand-100">
                                ${b.roast_level || "N/A"}
                            </span>
                        </div>
                        <p class="text-xs text-gray-400 mt-2 flex items-center gap-1">
                            <i data-lucide="globe" class="w-3 h-3"></i> ${b.origin || "Origem não informada"}
                        </p>
                    </div>
                `,
      )
      .join("");

    const cardHTML = `
                    <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300 flex flex-col h-full group">
                        <div class="card-header-gradient p-6 border-b border-gray-100 flex-shrink-0">
                            <div class="flex justify-between items-start mb-2">
                                <h3 class="text-xl font-bold text-gray-900 group-hover:text-brand-600 transition-colors">${cafe.name}</h3>
                                <div class="bg-white p-2 rounded-full shadow-sm">
                                    <i data-lucide="coffee" class="w-5 h-5 text-brand-500"></i>
                                </div>
                            </div>
                            <div class="flex items-center text-sm text-gray-600 gap-1.5 mt-2">
                                <i data-lucide="map-pin" class="w-4 h-4 text-gray-400"></i>
                                <span class="truncate" title="${cafe.location || "Localização desconhecida"}">
                                    ${cafe.location || "Localização desconhecida"}
                                </span>
                            </div>
                        </div>
                        
                        <div class="p-5 flex-grow bg-white">
                            ${
                              beans.length > 0
                                ? `<h4 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Grãos Disponíveis (${beans.length})</h4>
                                   <div class="flex flex-col gap-1">
                                        ${beanTags}
                                   </div>`
                                : `<p class="text-sm text-gray-400 italic text-center py-4">Nenhum grão inventariado no momento.</p>`
                            }
                        </div>
                    </div>
                `;
    list.insertAdjacentHTML("beforeend", cardHTML);
  });

  lucide.createIcons(); // Activate dynamically generated icons
}

function updateMarkers(cafes) {
  markers.forEach((m) => map.removeLayer(m));
  markers = [];

  cafes.forEach((cafe) => {
    // Mock coordinates based on SP (visual only, as there is no lat/long in current DB)
    const lat = -23.5505 + (Math.random() - 0.5) * 5;
    const lng = -46.6333 + (Math.random() - 0.5) * 5;

    const markerHtmlStyles = `
                    background-color: #e05d3a;
                    width: 1.5rem;
                    height: 1.5rem;
                    display: block;
                    left: -0.75rem;
                    top: -0.75rem;
                    position: relative;
                    border-radius: 50% 50% 50% 0;
                    transform: rotate(-45deg);
                    border: 2px solid white;
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                `;

    const customIcon = L.divIcon({
      className: "custom-pin",
      iconAnchor: [0, 24],
      popupAnchor: [0, -36],
      html: `<span style="${markerHtmlStyles}"></span>`,
    });

    const marker = L.marker([lat, lng], { icon: customIcon }).addTo(map)
      .bindPopup(`
                        <div class="font-sans">
                            <strong class="text-gray-900 block mb-1">${cafe.name}</strong>
                            <span class="text-xs text-gray-500">${cafe.location || ""}</span>
                        </div>
                    `);
    markers.push(marker);
  });

  if (markers.length > 0 && mapIsVisible) {
    const group = new L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.1));
  }
}

function getUserLocation() {
  if (!navigator.geolocation) {
    alert("Geolocalização não é suportada pelo seu navegador.");
    return;
  }

  const btn = document.getElementById("near-me-btn");
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Localizando...`;
  lucide.createIcons();

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;

      // Center on map
      map.setView([latitude, longitude], 13);

      // Open map if closed
      const mapContainer = document.getElementById("map-container");
      if (!mapContainer.classList.contains("open")) {
        document.getElementById("toggle-map-btn").click();
      }

      // Add a special marker for the user
      const userMarker = L.circleMarker([latitude, longitude], {
        radius: 8,
        fillColor: "#3b82f6",
        color: "#fff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8,
      })
        .addTo(map)
        .bindPopup("Você está aqui")
        .openPopup();

      btn.innerHTML = originalHtml;
      lucide.createIcons();
    },
    (err) => {
      console.error(err);
      alert("Não foi possível obter sua localização.");
      btn.innerHTML = originalHtml;
      lucide.createIcons();
    },
  );
}
