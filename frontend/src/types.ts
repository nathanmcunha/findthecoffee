// API Response types
export interface ApiResponse<T> {
  data: T[];
  page: number;
  per_page: number;
}

export interface Roaster {
  id: string;  // UUID
  name: string;
  website?: string | null;
  location?: string | null;
  address?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface Bean {
  id: string;  // UUID
  name: string;
  roast_level?: string | null;
  origin?: string | null;
  roaster_id?: string | null;
  roaster_name?: string | null;
  // Extended fields (may be added later)
  tasting_notes?: string[] | null;
  variety?: string | null;
  processing?: string | null;
  altitude?: number | null;
  acidity?: number | null;
  sweetness?: number | null;
  body?: number | null;
}

export interface Cafe {
  id: string;  // UUID
  name: string;
  location?: string | null;
  address?: string | null;
  website?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  relevance?: number;  // For search results
  matching_beans: Bean[];
}

export interface NearbyCafe extends Cafe {
  distance_m: number;
}
