import type { Cafe, NearbyCafe } from "./types.ts";

export let map: L.Map;
export let markers: L.Layer[] = [];

const DEFAULT_CENTER: L.LatLngTuple = [-23.5505, -46.6333]; // São Paulo
const DEFAULT_ZOOM = 5;

export function initMap(): void {
  map = L.map("map").setView(DEFAULT_CENTER, DEFAULT_ZOOM);
  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      r: window.devicePixelRatio > 1 ? "@2x" : "",
    },
  ).addTo(map);
}

/**
 * Creates a custom pin icon for Leaflet markers
 */
function createPinIcon(): L.DivIcon {
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
    html: `<span style="${pinStyle}"></span>`,
  });
}

/**
 * Updates map markers with cafe data
 * Uses real coordinates when available, falls back to random positions for testing
 */
export function updateMarkers(cafes: Cafe[], mapIsVisible: boolean): void {
  markers.forEach((m) => map.removeLayer(m));
  markers = [];

  cafes.forEach((cafe) => {
    // Use real coordinates if available, otherwise generate random position near São Paulo
    const lat = cafe.latitude ?? (DEFAULT_CENTER[0] + (Math.random() - 0.5) * 5);
    const lng = cafe.longitude ?? (DEFAULT_CENTER[1] + (Math.random() - 0.5) * 5);

    const icon = createPinIcon();

    // Build popup content with cafe details
    const popupContent = `
      <div style="font-family:'Manrope',sans-serif; min-width: 200px;">
        <strong style="color:#271310;display:block;margin-bottom:6px;font-size:14px;">${cafe.name}</strong>
        ${cafe.location ? `<div style="font-size:12px;color:#504442;margin-bottom:4px;">📍 ${cafe.location}</div>` : ""}
        ${cafe.address ? `<div style="font-size:11px;color:#666;margin-bottom:6px;">${cafe.address}</div>` : ""}
        ${cafe.website ? `<a href="${cafe.website}" target="_blank" style="font-size:12px;color:#271310;text-decoration:underline;">Visitar site</a>` : ""}
        ${(cafe as NearbyCafe).distance_m ? `<div style="font-size:11px;color:#271310;margin-top:6px;font-weight:600;">📏 ${(cafe as NearbyCafe).distance_m.toFixed(0)}m</div>` : ""}
      </div>
    `;

    const marker = L.marker([lat, lng], { icon })
      .addTo(map)
      .bindPopup(popupContent);
    
    markers.push(marker);
  });

  // Update badge text
  const badgeText = document.getElementById("map-badge-text");
  if (badgeText) {
    badgeText.textContent = `${cafes.length} ${cafes.length === 1 ? "local" : "locais"} no mapa`;
  }

  // Fit map to markers bounds if visible and has markers
  if (markers.length > 0 && mapIsVisible) {
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.1));
  }
}

/**
 * Gets user's current location and centers the map on it
 */
export function getUserLocation(): void {
  if (!navigator.geolocation) {
    alert("Geolocalização não é suportada pelo seu navegador.");
    return;
  }

  const btn = document.getElementById("near-me-btn") as HTMLButtonElement | null;
  if (!btn) return;
  
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Localizando...`;
  lucide.createIcons();

  navigator.geolocation.getCurrentPosition(
    async ({ coords: { latitude, longitude } }) => {
      // Center map on user location
      map.setView([latitude, longitude], 13);

      // Open map if not already open
      const mapContainer = document.getElementById("map-container");
      if (mapContainer && !mapContainer.classList.contains("open")) {
        (document.getElementById("toggle-map-btn") as HTMLButtonElement | null)?.click();
      }

      // Add user location marker
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

      // Fetch nearby cafes
      try {
        const { fetchNearbyCafes } = await import("./api.ts");
        const nearbyCafes = await fetchNearbyCafes(latitude, longitude, 5000);
        if (nearbyCafes.length > 0) {
          updateMarkers(nearbyCafes, true);
          // Trigger a refresh of the results list
          const event = new CustomEvent("nearby-loaded", { detail: nearbyCafes });
          window.dispatchEvent(event);
        }
      } catch (err) {
        console.error("Erro ao buscar cafés próximos:", err);
      }

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
