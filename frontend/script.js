lucide.createIcons();

document.fonts.ready.then(() => {
  document.body.classList.add("fonts-loaded");
});

const API_BASE_URL = "http://localhost:5000/api";
let map;
let markers = [];
let searchTimer;
let mapIsVisible = false;
let isFirstLoad = true;

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  fetchRoasters();
  fetchCafes();

  // Global search — debounced
  const globalSearch = document.getElementById("global-search");
  if (globalSearch) {
    globalSearch.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => fetchCafes(), 300);
    });
  }

  // Immediate select filters
  ["roaster-filter", "roast-filter"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", () => fetchCafes());
  });

  // Text filters with debounce (legacy hidden inputs)
  ["origin-filter", "cep-filter"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => fetchCafes(), 400);
      });
    }
  });

  // Near Me
  const nearMeBtn = document.getElementById("near-me-btn");
  if (nearMeBtn) nearMeBtn.addEventListener("click", getUserLocation);

  // Clear Filters
  const clearFilters = document.getElementById("clear-filters");
  if (clearFilters) {
    clearFilters.addEventListener("click", () => {
      document.getElementById("global-search").value = "";
      document.getElementById("roaster-filter").value = "";
      document.getElementById("roast-filter").value = "";
      document.getElementById("roaster-dropdown-label").textContent = "Todas as Torrefações";
      document.getElementById("roast-dropdown-label").textContent = "Qualquer Torra";
      fetchCafes();
    });
  }

  // Custom Dropdowns
  initCustomDropdowns();

  // Map Toggle
  const mapToggleBtn = document.getElementById("toggle-map-btn");
  const mapContainer = document.getElementById("map-container");
  const mapBtnText = document.getElementById("map-btn-text");
  const mapBadge = document.getElementById("map-badge");

  mapToggleBtn.addEventListener("click", () => {
    mapIsVisible = !mapIsVisible;
    if (mapIsVisible) {
      mapContainer.classList.add("open");
      mapBtnText.textContent = "Ocultar Mapa";
      mapToggleBtn.classList.add("bg-primary", "text-surface-container-lowest");
      mapToggleBtn.classList.remove("bg-surface-container", "text-primary");
      if (mapBadge) mapBadge.classList.remove("hidden");
      setTimeout(() => {
        map.invalidateSize();
        if (markers.length > 0) {
          const group = new L.featureGroup(markers);
          map.fitBounds(group.getBounds().pad(0.1));
        }
      }, 300);
    } else {
      mapContainer.classList.remove("open");
      mapBtnText.textContent = "Ver Mapa";
      mapToggleBtn.classList.remove("bg-primary", "text-surface-container-lowest");
      mapToggleBtn.classList.add("bg-surface-container", "text-primary");
      if (mapBadge) mapBadge.classList.add("hidden");
    }
  });
});

// ─── Custom Dropdowns ────────────────────────────────────────────────────────

function setDropdownOpen(btn, chevron, open) {
  if (open) {
    btn.classList.remove("rounded-md", "border-outline-variant/30", "hover:border-primary");
    btn.classList.add("rounded-t-md", "border-primary");
    chevron?.classList.add("rotate-180");
    chevron?.classList.remove("group-hover:translate-y-0.5");
  } else {
    btn.classList.remove("rounded-t-md", "border-primary");
    btn.classList.add("rounded-md", "border-outline-variant/30", "hover:border-primary");
    chevron?.classList.remove("rotate-180");
    chevron?.classList.add("group-hover:translate-y-0.5");
  }
}

function closeAllDropdowns() {
  [
    ["roaster-dropdown-btn", "roaster-dropdown-panel", "roaster-chevron"],
    ["roast-dropdown-btn",   "roast-dropdown-panel",   "roast-chevron"],
  ].forEach(([btnId, panelId, chevronId]) => {
    const panel = document.getElementById(panelId);
    if (panel && !panel.classList.contains("hidden")) {
      panel.classList.add("hidden");
      setDropdownOpen(document.getElementById(btnId), document.getElementById(chevronId), false);
    }
  });
}

function initCustomDropdowns() {
  [
    { btnId: "roaster-dropdown-btn", panelId: "roaster-dropdown-panel", labelId: "roaster-dropdown-label", selectId: "roaster-filter", chevronId: "roaster-chevron" },
    { btnId: "roast-dropdown-btn",   panelId: "roast-dropdown-panel",   labelId: "roast-dropdown-label",   selectId: "roast-filter",   chevronId: "roast-chevron"   },
  ].forEach(({ btnId, panelId, labelId, selectId, chevronId }) => {
    const btn    = document.getElementById(btnId);
    const panel  = document.getElementById(panelId);
    const label  = document.getElementById(labelId);
    const select = document.getElementById(selectId);
    const chevron = document.getElementById(chevronId);
    if (!btn || !panel) return;

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = !panel.classList.contains("hidden");
      closeAllDropdowns();
      if (!isOpen) {
        panel.classList.remove("hidden");
        setDropdownOpen(btn, chevron, true);
      }
    });

    panel.addEventListener("click", (e) => {
      const item = e.target.closest("[data-value]");
      if (!item) return;
      label.textContent = item.textContent.trim();
      select.value = item.dataset.value;
      select.dispatchEvent(new Event("change"));
      panel.classList.add("hidden");
      setDropdownOpen(btn, chevron, false);
    });
  });

  document.addEventListener("click", closeAllDropdowns);
}

// ─── Map ────────────────────────────────────────────────────────────────────

function initMap() {
  map = L.map("map").setView([-23.5505, -46.6333], 5);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: "&copy; OpenStreetMap &copy; CARTO",
    r: window.devicePixelRatio > 1 ? "@2x" : "",
  }).addTo(map);
}

function updateMarkers(venues) {
  markers.forEach((m) => map.removeLayer(m));
  markers = [];

  venues.forEach((venue) => {
    const lat = -23.5505 + (Math.random() - 0.5) * 5;
    const lng = -46.6333 + (Math.random() - 0.5) * 5;

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

    const icon = L.divIcon({
      className: "custom-pin",
      iconAnchor: [0, 24],
      popupAnchor: [0, -36],
      html: `<span style="${pinStyle}"></span>`,
    });

    const marker = L.marker([lat, lng], { icon })
      .addTo(map)
      .bindPopup(`
        <div style="font-family:'Manrope',sans-serif;">
          <strong style="color:#271310;display:block;margin-bottom:4px;">${venue.name}</strong>
          <span style="font-size:12px;color:#504442;">${venue.location || ""}</span>
        </div>
      `);
    markers.push(marker);
  });

  // Update badge count
  const badgeText = document.getElementById("map-badge-text");
  if (badgeText) {
    badgeText.textContent = `${venues.length} ${venues.length === 1 ? "local" : "locais"} no mapa`;
  }

  if (markers.length > 0 && mapIsVisible) {
    const group = new L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.1));
  }
}

// ─── Data Fetching ───────────────────────────────────────────────────────────

function fetchRoasters() {
  fetch(`${API_BASE_URL}/roasters`)
    .then((r) => r.json())
    .then((data) => {
      const select = document.getElementById("roaster-filter");
      const list = document.getElementById("roaster-dropdown-list");
      if (!select) return;
      while (select.options.length > 1) select.remove(1);
      if (list) while (list.children.length > 1) list.removeChild(list.lastChild);
      data.forEach((roaster) => {
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
    })
    .catch((err) => console.error("Erro ao buscar torrefações:", err));
}

function fetchCafes() {
  const query = document.getElementById("global-search").value;
  const roast = document.getElementById("roast-filter").value;
  const roasterId = document.getElementById("roaster-filter").value;

  const resultsList = document.getElementById("results-list");

  if (isFirstLoad) {
    isFirstLoad = false;
    resultsList.innerHTML = `
      <div class="col-span-full flex flex-col items-center py-16 gap-4">
        <div class="relative flex flex-col items-center">
          <span class="material-symbols-outlined text-4xl text-primary" style="visibility:visible">coffee_maker</span>
          <div class="w-0.5 bg-secondary/40 animate-drip my-1"></div>
          <span class="material-symbols-outlined text-2xl text-primary" style="visibility:visible">local_cafe</span>
        </div>
        <p class="text-on-surface-variant font-medium">Buscando o melhor café para você...</p>
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
    resultsList.innerHTML = skeletonCard + skeletonCard;
  }

  const params = [];
  if (query) params.push(`q=${encodeURIComponent(query)}`);
  if (roast) params.push(`roast=${roast}`);
  if (roasterId) params.push(`roaster_id=${roasterId}`);
  const qs = params.length ? `?${params.join("&")}` : "";

  fetch(`${API_BASE_URL}/cafes${qs}`)
    .then((r) => {
      if (!r.ok) throw new Error("Falha na resposta da rede");
      return r.json();
    })
    .then((data) => {
      renderResults(data);
      updateMarkers(data);
    })
    .catch((err) => {
      resultsList.innerHTML = `
        <div class="col-span-full py-12 text-center bg-surface-container-low rounded-2xl border border-outline-variant/20">
          <i data-lucide="alert-circle" class="w-10 h-10 text-error mx-auto mb-3"></i>
          <h3 class="text-lg font-medium text-on-surface">Erro ao carregar dados</h3>
          <p class="text-on-surface-variant mt-1 text-sm">O servidor backend está rodando?</p>
        </div>
      `;
      lucide.createIcons();
      console.error("Erro na API:", err);
    });
}

// ─── Rendering ───────────────────────────────────────────────────────────────

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

function renderGrainItem(bean, idx) {
  const id = `grain-${bean.id}`;
  const sensoryAcidity   = bean.acidity   ?? null;
  const sensorySweet     = bean.sweetness ?? null;
  const sensoryBody      = bean.body      ?? null;
  const hasSensory       = sensoryAcidity || sensorySweet || sensoryBody;

  const tastingNotes  = bean.tasting_notes  ? bean.tasting_notes.join(", ") : null;
  const variety       = bean.variety        ?? null;
  const process       = bean.processing     ?? null;
  const altitude      = bean.altitude       ? `${bean.altitude}m` : null;
  const roastProfile  = bean.roast_level    ?? null;

  const hasDetails = tastingNotes || variety || roastProfile || hasSensory;

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
              ${[bean.roaster_name, process, altitude].filter(Boolean).join(" · ") || "Detalhes não disponíveis"}
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
            ${variety ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Variedade</p>
                <p class="text-sm font-medium text-on-surface">${variety}</p>
              </div>
            ` : ""}
            ${roastProfile ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Torra</p>
                <p class="text-sm font-medium text-on-surface">${roastProfile}</p>
              </div>
            ` : ""}
            ${hasSensory ? `
              <div class="col-span-full bg-surface-container-high/40 p-3 rounded-lg flex justify-between">
                ${createSensoryBar("Acidez",  sensoryAcidity)}
                ${createSensoryBar("Doçura",  sensorySweet)}
                ${createSensoryBar("Corpo",   sensoryBody)}
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

  const beansHTML = beans.length > 0
    ? `
      <h4 class="text-xs font-bold text-primary mb-4 uppercase tracking-tighter">
        Grãos Disponíveis
      </h4>
      <div class="space-y-4">
        ${beans.map((bean, idx) => renderGrainItem(bean, idx)).join("")}
      </div>
    `
    : `<p class="text-sm text-on-surface-variant italic text-center py-6">Nenhum grão inventariado no momento.</p>`;

  return `
    <div class="bg-surface-container-low rounded-xl p-1 transition-all">
      <div class="bg-surface-container-lowest rounded-lg p-8 h-full flex flex-col">

        <div class="flex justify-between items-start mb-6">
          <div>
            <span class="text-xs font-bold tracking-widest uppercase text-on-surface-variant mb-2 block">
              ${venue.location || "Localização não informada"}
            </span>
            <h3 class="font-headline text-3xl text-primary mb-1">${venue.name}</h3>
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
        <h3 class="text-xl font-headline text-primary mb-2">Nenhum café encontrado</h3>
        <p class="text-on-surface-variant">Tente ajustar seus filtros ou termo de busca.</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  list.innerHTML = venues.map(renderVenueCard).join("");
  lucide.createIcons();
}

// ─── Grain Toggle ─────────────────────────────────────────────────────────────

window.toggleGrain = function (id) {
  const content = document.getElementById(`content-${id}`);
  const chevron = document.getElementById(`chevron-${id}`);
  if (content && chevron) {
    content.classList.toggle("expanded");
    chevron.classList.toggle("rotated");
  }
};

// ─── Geolocation ─────────────────────────────────────────────────────────────

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
    ({ coords: { latitude, longitude } }) => {
      map.setView([latitude, longitude], 13);

      const mapContainer = document.getElementById("map-container");
      if (!mapContainer.classList.contains("open")) {
        document.getElementById("toggle-map-btn").click();
      }

      L.circleMarker([latitude, longitude], {
        radius: 8,
        fillColor: "#271310",
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
