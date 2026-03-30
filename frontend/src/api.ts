import type { Cafe, Roaster } from "./types.ts";

const API_BASE_URL = "http://localhost:5000/api";

interface PaginatedResponse<T> {
  data: T[];
  page: number;
  per_page: number;
}

export async function fetchRoasters(): Promise<Roaster[]> {
  const r = await fetch(`${API_BASE_URL}/roasters`);
  const json = await r.json() as PaginatedResponse<Roaster>;
  return json.data;
}

export interface CafeFilters {
  query?: string;
  roast?: string;
  roasterId?: string;
}

export async function fetchCafes(filters: CafeFilters): Promise<Cafe[]> {
  const params: string[] = [];
  if (filters.query) params.push(`q=${encodeURIComponent(filters.query)}`);
  if (filters.roast) params.push(`roast=${filters.roast}`);
  if (filters.roasterId) params.push(`roaster_id=${filters.roasterId}`);
  const qs = params.length ? `?${params.join("&")}` : "";

  const r = await fetch(`${API_BASE_URL}/cafes${qs}`);
  if (!r.ok) throw new Error("Falha na resposta da rede");
  const json = await r.json() as PaginatedResponse<Cafe>;
  return json.data;
}
