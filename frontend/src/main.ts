import { fetchCafes, fetchRoasters } from "./api.ts";
import { initMap, updateMarkers, getUserLocation } from "./map.ts";
import { renderResults, showLoadingState, showErrorState } from "./ui.ts";
import type { Cafe } from "./types.ts";

// Initialize Lucide icons
lucide.createIcons();

// Wait for fonts to load
document.fonts.ready.then(() => {
  document.body.classList.add("fonts-loaded");
});

let searchTimer: ReturnType<typeof setTimeout>;
let mapIsVisible = false;
let isFirstLoad = true;
let currentCafes: Cafe[] = [];

interface Filters {
  query: string;
  roast: string;
  origin: string;
  roasterId: string;
  name: string;
}

function getFilters(): Filters {
  return {
    query: document.getElementById("global-search")?.value ?? "",
    roast: document.getElementById("roast-filter")?.value ?? "",
    origin: document.getElementById("origin-filter")?.value ?? "",
    roasterId: document.getElementById("roaster-filter")?.value ?? "",
    name: document.getElementById("name-filter")?.value ?? "",
  };
}

async function loadCafes(): Promise<void> {
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

// Listen for nearby cafes loaded event
window.addEventListener("nearby-loaded", ((event: CustomEvent<Cafe[]>) => {
  currentCafes = event.detail;
  renderResults(event.detail);
}) as EventListener);

document.addEventListener("DOMContentLoaded", () => {
  // Initialize map
  initMap();
  
  // Load roasters for dropdown
  fetchRoasters()
    .then((roasters) => {
      const select = document.getElementById("roaster-filter") as HTMLSelectElement;
      const list = document.getElementById("roaster-dropdown-list");
      
      if (select) {
        // Clear existing options except the first one
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
    })
    .catch((err) => console.error("Erro ao buscar torrefações:", err));
  
  // Initial load of cafes
  loadCafes();
  
  // Global search with debounce
  const globalSearch = document.getElementById("global-search");
  if (globalSearch) {
    globalSearch.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(loadCafes, 300);
    });
  }
  
  // Filter dropdowns
  ["roaster-filter", "roast-filter", "origin-filter"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", loadCafes);
  });
  
  // Hidden legacy filters
  ["cep-filter"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(loadCafes, 400);
      });
    }
  });
  
  // Near me button
  const nearMeBtn = document.getElementById("near-me-btn");
  if (nearMeBtn) nearMeBtn.addEventListener("click", getUserLocation);
  
  // Clear filters button
  const clearFilters = document.getElementById("clear-filters");
  if (clearFilters) {
    clearFilters.addEventListener("click", () => {
      const globalSearchEl = document.getElementById("global-search") as HTMLInputElement;
      const roasterFilter = document.getElementById("roaster-filter") as HTMLSelectElement;
      const roastFilter = document.getElementById("roast-filter") as HTMLSelectElement;
      
      if (globalSearchEl) globalSearchEl.value = "";
      if (roasterFilter) roasterFilter.value = "";
      if (roastFilter) roastFilter.value = "";
      
      const roasterLabel = document.getElementById("roaster-dropdown-label");
      if (roasterLabel) roasterLabel.textContent = "Todas as Torrefações";
      
      const roastLabel = document.getElementById("roast-dropdown-label");
      if (roastLabel) roastLabel.textContent = "Qualquer Torra";
      
      loadCafes();
    });
  }
  
  // Map toggle
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

// Global function for toggling grain details
declare global {
  interface Window {
    toggleGrain: (id: string) => void;
  }
}

window.toggleGrain = function(id: string) {
  const content = document.getElementById(`content-${id}`);
  const chevron = document.getElementById(`chevron-${id}`);
  if (content && chevron) {
    content.classList.toggle("expanded");
    chevron.classList.toggle("rotated");
  }
};

// Export for access in script.js
(window as any).markers = markers;
(window as any).map = map;
