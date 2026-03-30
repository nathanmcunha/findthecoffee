import type { Cafe } from "./types.ts";

export let map: L.Map;
export let markers: L.Layer[] = [];

export function initMap(): void {
  map = L.map("map").setView([-23.5505, -46.6333], 5);
  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      r: window.devicePixelRatio > 1 ? "@2x" : "",
    },
  ).addTo(map);
}

export function updateMarkers(venues: Cafe[], mapIsVisible: boolean): void {
  markers.forEach((m) => map.removeLayer(m));
  markers = [];

  venues.forEach((venue) => {
    // Use actual coordinates if available, otherwise use random fallback
    const lat = venue.latitude ?? (-23.5505 + (Math.random() - 0.5) * 5);
    const lng = venue.longitude ?? (-46.6333 + (Math.random() - 0.5) * 5);

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

    const marker = L.marker([lat, lng], { icon }).addTo(map).bindPopup(`
        <div style="font-family:'Manrope',sans-serif;">
          <strong style="color:#271310;display:block;margin-bottom:4px;">${venue.name}</strong>
          <span style="font-size:12px;color:#504442;">${venue.location || ""}</span>
        </div>
      `);
    markers.push(marker);
  });

  const badgeText = document.getElementById("map-badge-text");
  if (badgeText) {
    badgeText.textContent = `${venues.length} ${venues.length === 1 ? "local" : "locais"} no mapa`;
  }

  if (markers.length > 0 && mapIsVisible) {
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.1));
  }
}

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
    ({ coords: { latitude, longitude } }) => {
      map.setView([latitude, longitude], 13);

      const mapContainer = document.getElementById("map-container");
      if (mapContainer && !mapContainer.classList.contains("open")) {
        (document.getElementById("toggle-map-btn") as HTMLButtonElement | null)?.click();
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
