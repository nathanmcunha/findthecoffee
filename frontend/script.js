"use strict";
(() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __esm = (fn, res) => function __init() {
    return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
  };
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };

  // frontend/src/api.ts
  var api_exports = {};
  __export(api_exports, {
    fetchCafes: () => fetchCafes,
    fetchNearbyCafes: () => fetchNearbyCafes,
    fetchRoasters: () => fetchRoasters
  });
  async function fetchRoasters() {
    const r = await fetch(`${API_BASE_URL}/roasters`);
    if (!r.ok) throw new Error("Falha ao buscar torrefa\xE7\xF5es");
    const json = await r.json();
    return json.data;
  }
  async function fetchCafes(filters = {}) {
    const params = [];
    if (filters.query) params.push(`q=${encodeURIComponent(filters.query)}`);
    if (filters.roast) params.push(`roast=${encodeURIComponent(filters.roast)}`);
    if (filters.origin) params.push(`origin=${encodeURIComponent(filters.origin)}`);
    if (filters.roasterId) params.push(`roaster_id=${filters.roasterId}`);
    if (filters.name) params.push(`name=${encodeURIComponent(filters.name)}`);
    if (filters.page) params.push(`page=${filters.page}`);
    if (filters.per_page) params.push(`per_page=${filters.per_page}`);
    const qs = params.length ? `?${params.join("&")}` : "";
    const r = await fetch(`${API_BASE_URL}/cafes${qs}`);
    if (!r.ok) throw new Error("Falha na resposta da rede");
    const json = await r.json();
    return json.data;
  }
  async function fetchNearbyCafes(lat, lng, radius = 5e3) {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lng: lng.toString(),
      radius: radius.toString()
    });
    const r = await fetch(`${API_BASE_URL}/cafes/nearby?${params}`);
    if (!r.ok) throw new Error("Falha ao buscar caf\xE9s pr\xF3ximos");
    return r.json();
  }
  var API_BASE_URL;
  var init_api = __esm({
    "frontend/src/api.ts"() {
      "use strict";
      API_BASE_URL = "http://localhost:5000/api";
    }
  });

  // frontend/src/main.ts
  init_api();

  // frontend/src/map.ts
  var map2;
  var markers2 = [];
  var DEFAULT_CENTER = [-23.5505, -46.6333];
  var DEFAULT_ZOOM = 5;
  function initMap() {
    map2 = L.map("map").setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      {
        attribution: "&copy; OpenStreetMap &copy; CARTO",
        r: window.devicePixelRatio > 1 ? "@2x" : ""
      }
    ).addTo(map2);
  }
  function createPinIcon() {
    const pinStyle = `
    background-color: #271310;
    width: 1.5rem; height: 1.5rem;
    display: block;
    left: -0.75rem; top: -0.75rem;
    position: relative;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 2px solid white;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
  `;
    return L.divIcon({
      className: "custom-pin",
      iconAnchor: [0, 24],
      popupAnchor: [0, -36],
      html: `<span style="${pinStyle}"></span>`
    });
  }
  function updateMarkers(cafes, mapIsVisible2) {
    markers2.forEach((m) => map2.removeLayer(m));
    markers2 = [];
    cafes.forEach((cafe) => {
      const lat = cafe.latitude ?? DEFAULT_CENTER[0] + (Math.random() - 0.5) * 5;
      const lng = cafe.longitude ?? DEFAULT_CENTER[1] + (Math.random() - 0.5) * 5;
      const icon = createPinIcon();
      const popupContent = `
      <div style="font-family:'Manrope',sans-serif; min-width: 200px;">
        <strong style="color:#271310;display:block;margin-bottom:6px;font-size:14px;">${cafe.name}</strong>
        ${cafe.location ? `<div style="font-size:12px;color:#504442;margin-bottom:4px;">\u{1F4CD} ${cafe.location}</div>` : ""}
        ${cafe.address ? `<div style="font-size:11px;color:#666;margin-bottom:6px;">${cafe.address}</div>` : ""}
        ${cafe.website ? `<a href="${cafe.website}" target="_blank" style="font-size:12px;color:#271310;text-decoration:underline;">Visitar site</a>` : ""}
        ${cafe.distance_m ? `<div style="font-size:11px;color:#271310;margin-top:6px;font-weight:600;">\u{1F4CF} ${cafe.distance_m.toFixed(0)}m</div>` : ""}
      </div>
    `;
      const marker = L.marker([lat, lng], { icon }).addTo(map2).bindPopup(popupContent);
      markers2.push(marker);
    });
    const badgeText = document.getElementById("map-badge-text");
    if (badgeText) {
      badgeText.textContent = `${cafes.length} ${cafes.length === 1 ? "local" : "locais"} no mapa`;
    }
    if (markers2.length > 0 && mapIsVisible2) {
      const group = L.featureGroup(markers2);
      map2.fitBounds(group.getBounds().pad(0.1));
    }
  }
  function getUserLocation() {
    if (!navigator.geolocation) {
      alert("Geolocaliza\xE7\xE3o n\xE3o \xE9 suportada pelo seu navegador.");
      return;
    }
    const btn = document.getElementById("near-me-btn");
    if (!btn) return;
    const originalHtml = btn.innerHTML;
    btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Localizando...`;
    lucide.createIcons();
    navigator.geolocation.getCurrentPosition(
      async ({ coords: { latitude, longitude } }) => {
        map2.setView([latitude, longitude], 13);
        const mapContainer = document.getElementById("map-container");
        if (mapContainer && !mapContainer.classList.contains("open")) {
          document.getElementById("toggle-map-btn")?.click();
        }
        L.circleMarker([latitude, longitude], {
          radius: 8,
          fillColor: "#271310",
          color: "#fff",
          weight: 2,
          opacity: 1,
          fillOpacity: 0.8
        }).addTo(map2).bindPopup("Voc\xEA est\xE1 aqui").openPopup();
        try {
          const { fetchNearbyCafes: fetchNearbyCafes2 } = await Promise.resolve().then(() => (init_api(), api_exports));
          const nearbyCafes = await fetchNearbyCafes2(latitude, longitude, 5e3);
          if (nearbyCafes.length > 0) {
            updateMarkers(nearbyCafes, true);
            const event = new CustomEvent("nearby-loaded", { detail: nearbyCafes });
            window.dispatchEvent(event);
          }
        } catch (err) {
          console.error("Erro ao buscar caf\xE9s pr\xF3ximos:", err);
        }
        btn.innerHTML = originalHtml;
        lucide.createIcons();
      },
      (err) => {
        console.error(err);
        alert("N\xE3o foi poss\xEDvel obter sua localiza\xE7\xE3o.");
        btn.innerHTML = originalHtml;
        lucide.createIcons();
      }
    );
  }

  // frontend/src/ui.ts
  function createSensoryBar(label, value) {
    if (!value) return "";
    let dots = "";
    for (let i = 1; i <= 5; i++) {
      dots += `<div class="w-3 h-1 rounded-full ${i <= value ? "bg-primary" : "bg-outline-variant"}"></div>`;
    }
    return `
    <div class="text-center px-4 border-r border-outline-variant/20 last:border-r-0">
      <p class="text-[10px] uppercase font-bold mb-1">${label}</p>
      <div class="flex gap-0.5">${dots}</div>
    </div>
  `;
  }
  function renderGrainItem(bean, cafeId, idx) {
    const id = `grain-${cafeId}-${bean.id}`;
    const hasSensory = bean.acidity || bean.sweetness || bean.body;
    const tastingNotes = bean.tasting_notes ? bean.tasting_notes.join(", ") : null;
    const altitude = bean.altitude ? `${bean.altitude}m` : null;
    const hasDetails = tastingNotes || bean.variety || bean.roast_level || hasSensory;
    return `
    <div class="group border border-outline-variant/15 rounded-xl p-5 hover:bg-surface-container-low transition-all ${hasDetails ? "cursor-pointer" : ""}"
         ${hasDetails ? `onclick="toggleGrain('${id}')"` : ""}>

      <div class="flex justify-between items-center">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-lg bg-surface-container overflow-hidden flex items-center justify-center flex-shrink-0">
            <i data-lucide="coffee" class="w-5 h-5 text-on-surface-variant"></i>
          </div>
          <div>
            <p class="font-bold text-primary text-sm">${bean.name}</p>
            <p class="text-xs text-on-surface-variant uppercase">
              ${[bean.roaster_name, bean.roast_level, bean.origin].filter(Boolean).join(" \xB7 ") || "Detalhes n\xE3o dispon\xEDveis"}
            </p>
          </div>
        </div>
        ${hasDetails ? `
          <i data-lucide="chevron-down" id="chevron-${id}"
             class="chevron-icon w-5 h-5 text-outline-variant group-hover:text-primary transition-colors flex-shrink-0 ${idx === 0 ? "rotated" : ""}"></i>
        ` : ""}
      </div>

      ${hasDetails ? `
        <div id="content-${id}" class="grain-content ${idx === 0 ? "expanded" : ""}">
          <div class="mt-6 pt-6 border-t border-outline-variant/10 grid grid-cols-2 md:grid-cols-3 gap-y-6 gap-x-4">
            ${tastingNotes ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Notas de Sabor</p>
                <p class="text-sm font-medium text-on-surface">${tastingNotes}</p>
              </div>
            ` : ""}
            ${bean.variety ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Variedade</p>
                <p class="text-sm font-medium text-on-surface">${bean.variety}</p>
              </div>
            ` : ""}
            ${bean.roast_level ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Torra</p>
                <p class="text-sm font-medium text-on-surface">${bean.roast_level}</p>
              </div>
            ` : ""}
            ${bean.origin ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Origem</p>
                <p class="text-sm font-medium text-on-surface">${bean.origin}</p>
              </div>
            ` : ""}
            ${hasSensory ? `
              <div class="col-span-full bg-surface-container-high/40 p-3 rounded-lg flex justify-between">
                ${createSensoryBar("Acidez", bean.acidity)}
                ${createSensoryBar("Do\xE7ura", bean.sweetness)}
                ${createSensoryBar("Corpo", bean.body)}
              </div>
            ` : ""}
          </div>
        </div>
      ` : ""}
    </div>
  `;
  }
  function renderVenueCard(venue) {
    const beans = venue.matching_beans || [];
    const beansHTML = beans.length > 0 ? `
      <h4 class="text-xs font-bold text-primary mb-4 uppercase tracking-tighter">
        Gr\xE3os Dispon\xEDveis
      </h4>
      <div class="space-y-4">
        ${beans.map((bean, idx) => renderGrainItem(bean, venue.id, idx)).join("")}
      </div>
    ` : `<p class="text-sm text-on-surface-variant italic text-center py-6">Nenhum gr\xE3o inventariado no momento.</p>`;
    return `
    <div class="bg-surface-container-low rounded-xl p-1 transition-all">
      <div class="bg-surface-container-lowest rounded-lg p-8 h-full flex flex-col">

        <div class="flex justify-between items-start mb-6">
          <div class="flex-1">
            <span class="text-xs font-bold tracking-widest uppercase text-on-surface-variant mb-2 block">
              ${venue.location || "Localiza\xE7\xE3o n\xE3o informada"}
            </span>
            <h3 class="font-headline text-3xl text-primary mb-1">${venue.name}</h3>
            ${venue.address ? `
              <p class="text-sm text-on-surface-variant mt-2 flex items-center gap-1">
                <i data-lucide="map-pin" class="w-4 h-4"></i>
                ${venue.address}
              </p>
            ` : ""}
            ${venue.website ? `
              <a href="${venue.website}" target="_blank" rel="noopener noreferrer" 
                 class="text-sm text-primary hover:underline mt-1 inline-flex items-center gap-1">
                <i data-lucide="external-link" class="w-3 h-3"></i>
                Visitar site
              </a>
            ` : ""}
          </div>
          <div class="bg-secondary-container p-3 rounded-lg text-on-secondary-container flex-shrink-0">
            <i data-lucide="coffee" class="w-6 h-6"></i>
          </div>
        </div>

        <div class="mt-auto">
          ${beansHTML}
        </div>

      </div>
    </div>
  `;
  }
  function renderResults(venues) {
    const countEl = document.getElementById("results-count");
    if (countEl) {
      countEl.textContent = `${venues.length} ${venues.length === 1 ? "encontrado" : "encontrados"}`;
    }
    const list = document.getElementById("results-list");
    if (!list) return;
    if (venues.length === 0) {
      list.innerHTML = `
      <div class="col-span-full py-16 text-center">
        <div class="bg-surface-container rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
          <i data-lucide="coffee" class="w-10 h-10 text-on-surface-variant"></i>
        </div>
        <h3 class="text-xl font-headline text-primary mb-2">Nenhum caf\xE9 encontrado</h3>
        <p class="text-on-surface-variant">Tente ajustar seus filtros ou termo de busca.</p>
      </div>
    `;
      lucide.createIcons();
      return;
    }
    list.innerHTML = venues.map(renderVenueCard).join("");
    lucide.createIcons();
  }
  function showLoadingState(isFirstLoad2) {
    const list = document.getElementById("results-list");
    if (!list) return;
    if (isFirstLoad2) {
      list.innerHTML = `
      <div class="col-span-full flex flex-col items-center py-16 gap-4">
        <div class="relative flex flex-col items-center">
          <span class="material-symbols-outlined text-4xl text-primary" style="visibility:visible">coffee_maker</span>
          <div class="w-0.5 bg-secondary/40 animate-drip my-1"></div>
          <span class="material-symbols-outlined text-2xl text-primary" style="visibility:visible">local_cafe</span>
        </div>
        <p class="text-on-surface-variant font-medium">Buscando o melhor caf\xE9 para voc\xEA...</p>
      </div>
    `;
    } else {
      const skeletonCard = `
      <div class="bg-surface-container-lowest p-8 rounded-xl shadow-sm space-y-4">
        <div class="flex justify-between items-start">
          <div class="space-y-2 flex-1">
            <div class="h-6 w-3/4 bg-surface-container-high rounded skeleton-shimmer"></div>
            <div class="h-4 w-1/2 bg-surface-container-high rounded skeleton-shimmer"></div>
          </div>
          <div class="h-6 w-16 bg-surface-container-high rounded-full skeleton-shimmer ml-4"></div>
        </div>
        <div class="h-24 bg-surface-container-high rounded-lg skeleton-shimmer"></div>
        <div class="flex gap-2">
          <div class="h-4 w-16 bg-surface-container-high rounded skeleton-shimmer"></div>
          <div class="h-4 w-16 bg-surface-container-high rounded skeleton-shimmer"></div>
        </div>
      </div>
    `;
      list.innerHTML = skeletonCard + skeletonCard;
    }
  }
  function showErrorState() {
    const list = document.getElementById("results-list");
    if (!list) return;
    list.innerHTML = `
    <div class="col-span-full py-12 text-center bg-surface-container-low rounded-2xl border border-outline-variant/20">
      <i data-lucide="alert-circle" class="w-10 h-10 text-error mx-auto mb-3"></i>
      <h3 class="text-lg font-medium text-on-surface">Erro ao carregar dados</h3>
      <p class="text-on-surface-variant mt-1 text-sm">O servidor backend est\xE1 rodando?</p>
    </div>
  `;
    lucide.createIcons();
  }

  // frontend/src/main.ts
  lucide.createIcons();
  document.fonts.ready.then(() => {
    document.body.classList.add("fonts-loaded");
  });
  var searchTimer;
  var mapIsVisible = false;
  var isFirstLoad = true;
  var currentCafes = [];
  function getFilters() {
    return {
      query: document.getElementById("global-search")?.value ?? "",
      roast: document.getElementById("roast-filter")?.value ?? "",
      origin: document.getElementById("origin-filter")?.value ?? "",
      roasterId: document.getElementById("roaster-filter")?.value ?? "",
      name: document.getElementById("name-filter")?.value ?? ""
    };
  }
  async function loadCafes() {
    showLoadingState(isFirstLoad);
    if (isFirstLoad) isFirstLoad = false;
    try {
      const data = await fetchCafes(getFilters());
      currentCafes = data;
      renderResults(data);
      updateMarkers(data, mapIsVisible);
      console.log("Cafes loaded:", data);
    } catch (err) {
      showErrorState();
      console.error("Erro na API:", err);
    }
  }
  window.addEventListener("nearby-loaded", (event) => {
    currentCafes = event.detail;
    renderResults(event.detail);
  });
  document.addEventListener("DOMContentLoaded", () => {
    initMap();
    fetchRoasters().then((roasters) => {
      const select = document.getElementById("roaster-filter");
      const list = document.getElementById("roaster-dropdown-list");
      if (select) {
        while (select.options.length > 1) select.remove(1);
        if (list) while (list.children.length > 1) list.removeChild(list.lastChild);
        roasters.forEach((roaster) => {
          const opt = document.createElement("option");
          opt.value = roaster.id;
          opt.textContent = roaster.name;
          select.appendChild(opt);
          if (list) {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "px-6 py-3 text-left font-body text-sm text-on-surface hover:bg-surface-container-high transition-colors border-b border-outline-variant/10";
            btn.dataset.value = roaster.id;
            btn.textContent = roaster.name;
            list.appendChild(btn);
          }
        });
      }
    }).catch((err) => console.error("Erro ao buscar torrefa\xE7\xF5es:", err));
    loadCafes();
    const globalSearch = document.getElementById("global-search");
    if (globalSearch) {
      globalSearch.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(loadCafes, 300);
      });
    }
    ["roaster-filter", "roast-filter", "origin-filter"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", loadCafes);
    });
    ["cep-filter"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener("input", () => {
          clearTimeout(searchTimer);
          searchTimer = setTimeout(loadCafes, 400);
        });
      }
    });
    const nearMeBtn = document.getElementById("near-me-btn");
    if (nearMeBtn) nearMeBtn.addEventListener("click", getUserLocation);
    const clearFilters = document.getElementById("clear-filters");
    if (clearFilters) {
      clearFilters.addEventListener("click", () => {
        const globalSearchEl = document.getElementById("global-search");
        const roasterFilter = document.getElementById("roaster-filter");
        const roastFilter = document.getElementById("roast-filter");
        if (globalSearchEl) globalSearchEl.value = "";
        if (roasterFilter) roasterFilter.value = "";
        if (roastFilter) roastFilter.value = "";
        const roasterLabel = document.getElementById("roaster-dropdown-label");
        if (roasterLabel) roasterLabel.textContent = "Todas as Torrefa\xE7\xF5es";
        const roastLabel = document.getElementById("roast-dropdown-label");
        if (roastLabel) roastLabel.textContent = "Qualquer Torra";
        loadCafes();
      });
    }
    const mapToggleBtn = document.getElementById("toggle-map-btn");
    const mapContainer = document.getElementById("map-container");
    const mapBtnText = document.getElementById("map-btn-text");
    const mapBadge = document.getElementById("map-badge");
    if (mapToggleBtn) {
      mapToggleBtn.addEventListener("click", () => {
        mapIsVisible = !mapIsVisible;
        if (mapIsVisible) {
          mapContainer?.classList.add("open");
          if (mapBtnText) mapBtnText.textContent = "Ocultar Mapa";
          mapToggleBtn.classList.add("bg-primary", "text-surface-container-lowest");
          mapToggleBtn.classList.remove("bg-surface-container", "text-primary");
          mapBadge?.classList.remove("hidden");
          setTimeout(() => {
            map.invalidateSize();
            if (markers.length > 0) {
              const group = L.featureGroup(markers);
              map.fitBounds(group.getBounds().pad(0.1));
            }
          }, 300);
        } else {
          mapContainer?.classList.remove("open");
          if (mapBtnText) mapBtnText.textContent = "Ver Mapa";
          mapToggleBtn.classList.remove("bg-primary", "text-surface-container-lowest");
          mapToggleBtn.classList.add("bg-surface-container", "text-primary");
          mapBadge?.classList.add("hidden");
        }
      });
    }
  });
  window.toggleGrain = function(id) {
    const content = document.getElementById(`content-${id}`);
    const chevron = document.getElementById(`chevron-${id}`);
    if (content && chevron) {
      content.classList.toggle("expanded");
      chevron.classList.toggle("rotated");
    }
  };
  window.markers = markers;
  window.map = map;
})();
