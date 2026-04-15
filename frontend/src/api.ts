import type { Cafe, Roaster } from "./types.ts";

const API_BASE_URL: string = __API_BASE_URL__;

interface PaginatedResponse<T> {
  data: T[];
  page: number;
  per_page: number;
}

export async function fetchRoasters(
  signal?: AbortSignal | null,
): Promise<Roaster[]> {
  const opts = signal !== undefined ? { signal } : {};
  const r = await fetch(`${API_BASE_URL}/roasters`, opts);
  if (!r.ok) throw new Error("Falha ao buscar torrefações");
  const json = await r.json() as PaginatedResponse<Roaster>;
  return json.data;
}

export interface CafeFilters {
  query?: string;
  roast?: string;
  roasterId?: string;
}

export async function fetchCafes(
  filters: CafeFilters,
  signal?: AbortSignal | null,
): Promise<Cafe[]> {
  const params: string[] = [];
  if (filters.query) params.push(`q=${encodeURIComponent(filters.query)}`);
  if (filters.roast) params.push(`roast=${filters.roast}`);
  if (filters.roasterId) params.push(`roaster_id=${filters.roasterId}`);
  const qs = params.length ? `?${params.join("&")}` : "";

  const opts = signal !== undefined ? { signal } : {};
  const r = await fetch(`${API_BASE_URL}/cafes${qs}`, opts);
  if (!r.ok) throw new Error("Falha na resposta da rede");
  const json = await r.json() as PaginatedResponse<Cafe>;
  return json.data;
}
