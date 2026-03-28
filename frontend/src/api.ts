import type { ApiResponse, Cafe, Roaster, NearbyCafe } from "./types.ts";

const API_BASE_URL = "http://localhost:5000/api";

export async function fetchRoasters(): Promise<Roaster[]> {
  const r = await fetch(`${API_BASE_URL}/roasters`);
  if (!r.ok) throw new Error("Falha ao buscar torrefações");
  const json = await r.json();
  return json.data as Roaster[];
}

export interface CafeFilters {
  query?: string;
  roast?: string;
  origin?: string;
  roasterId?: string;
  name?: string;
  page?: number;
  per_page?: number;
}

export async function fetchCafes(filters: CafeFilters = {}): Promise<Cafe[]> {
  const params: string[] = [];
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
  return json.data as Cafe[];
}

export async function fetchNearbyCafes(lat: number, lng: number, radius: number = 5000): Promise<NearbyCafe[]> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lng: lng.toString(),
    radius: radius.toString()
  });
  
  const r = await fetch(`${API_BASE_URL}/cafes/nearby?${params}`);
  if (!r.ok) throw new Error("Falha ao buscar cafés próximos");
  return r.json() as Promise<NearbyCafe[]>;
}
