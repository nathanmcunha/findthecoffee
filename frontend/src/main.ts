/// <reference path="./globals.d.ts" />
/// <reference path="./leaflet.d.ts" />

import { fetchCafes, fetchRoasters } from "./api.ts";
import { getUserLocation, initMap, map, markers, updateMarkers } from "./map.ts";
import { initCustomDropdowns, populateRoasterDropdown } from "./dropdowns.ts";
import { renderResults, showErrorState, showLoadingState } from "./ui.ts";

lucide.createIcons();

document.fonts.ready.then(() => {
  document.body.classList.add("fonts-loaded");
});

let searchTimer: ReturnType<typeof setTimeout> | undefined;
let mapIsVisible = false;
let isFirstLoad = true;

function getFilters() {
  return {
    query: (document.getElementById("global-search") as HTMLInputElement | null)?.value ?? "",
    roast: (document.getElementById("roast-filter") as HTMLSelectElement | null)?.value ?? "",
    roasterId: (document.getElementById("roaster-filter") as HTMLSelectElement | null)?.value ?? "",
  };
}

async function loadCafes(): Promise<void> {
  showLoadingState(isFirstLoad);
  if (isFirstLoad) isFirstLoad = false;

  try {
    const data = await fetchCafes(getFilters());
    renderResults(data);
    updateMarkers(data, mapIsVisible);
    console.log(data);
  } catch (err) {
    showErrorState();
    console.error("Erro na API:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initMap();

  fetchRoasters()
    .then(populateRoasterDropdown)
    .catch((err) => console.error("Erro ao buscar torrefações:", err));

  loadCafes();

  const globalSearch = document.getElementById("global-search");
  if (globalSearch) {
    globalSearch.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(loadCafes, 300);
    });
  }

  ["roaster-filter", "roast-filter"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", loadCafes);
  });

  ["origin-filter", "cep-filter"].forEach((id) => {
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
      (document.getElementById("global-search") as HTMLInputElement).value = "";
      (document.getElementById("roaster-filter") as HTMLSelectElement).value = "";
      (document.getElementById("roast-filter") as HTMLSelectElement).value = "";
      const roasterLabel = document.getElementById("roaster-dropdown-label");
      if (roasterLabel) roasterLabel.textContent = "Todas as Torrefações";
      const roastLabel = document.getElementById("roast-dropdown-label");
      if (roastLabel) roastLabel.textContent = "Qualquer Torra";
      loadCafes();
    });
  }

  initCustomDropdowns();

  const mapToggleBtn = document.getElementById("toggle-map-btn");
  const mapContainer = document.getElementById("map-container");
  const mapBtnText = document.getElementById("map-btn-text");
  const mapBadge = document.getElementById("map-badge");

  if (!mapToggleBtn) return;

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
});

// Exposed globally for inline onclick handlers in rendered HTML
(window as unknown as Record<string, unknown>)["toggleGrain"] = function (id: string): void {
  const content = document.getElementById(`content-${id}`);
  const chevron = document.getElementById(`chevron-${id}`);
  if (content && chevron) {
    content.classList.toggle("expanded");
    chevron.classList.toggle("rotated");
  }
};
