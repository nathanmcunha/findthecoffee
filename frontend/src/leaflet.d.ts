// Minimal ambient declarations for Leaflet loaded via CDN <script> tag.
// Only covers the subset used in this project.

declare namespace L {
  interface MapOptions {
    [key: string]: unknown;
  }

  interface TileLayerOptions {
    attribution?: string;
    r?: string;
    [key: string]: unknown;
  }

  interface MarkerOptions {
    icon?: DivIcon;
    [key: string]: unknown;
  }

  interface DivIconOptions {
    className?: string;
    iconAnchor?: [number, number];
    popupAnchor?: [number, number];
    html?: string;
  }

  interface CircleMarkerOptions {
    radius?: number;
    fillColor?: string;
    color?: string;
    weight?: number;
    opacity?: number;
    fillOpacity?: number;
  }

  interface LatLngBoundsExpression {
    pad(amount: number): LatLngBoundsExpression;
  }

  interface Layer {
    addTo(map: Map): this;
    bindPopup(content: string): this;
    openPopup(): this;
    remove(): void;
  }

  interface Marker extends Layer {}
  interface CircleMarker extends Layer {}
  interface TileLayer extends Layer {}
  interface FeatureGroup extends Layer {
    getBounds(): LatLngBoundsExpression;
  }

  interface DivIcon {
    [key: string]: unknown;
  }

  interface Map {
    setView(latlng: [number, number], zoom: number): this;
    invalidateSize(): void;
    fitBounds(bounds: LatLngBoundsExpression): void;
    removeLayer(layer: Layer): void;
  }
}

// Declare L as a value (namespace + variable merge)
declare const L: {
  map(id: string, options?: L.MapOptions): L.Map;
  tileLayer(urlTemplate: string, options?: L.TileLayerOptions): L.TileLayer;
  marker(latlng: [number, number], options?: L.MarkerOptions): L.Marker;
  circleMarker(
    latlng: [number, number],
    options?: L.CircleMarkerOptions,
  ): L.CircleMarker;
  divIcon(options?: L.DivIconOptions): L.DivIcon;
  featureGroup(layers: L.Layer[]): L.FeatureGroup;
};
