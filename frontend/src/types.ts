export interface Roaster {
  id: string;
  name: string;
  website: string | null;
  location: string | null;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  updated_at: string;
}

export interface Bean {
  id: string;
  name: string;
  roast_level: string | null;
  origin: string | null;
  roaster_id: string | null;
  roaster_name: string | null;
  // Technical details (ficha técnica)
  variety: string | null;
  processing: string | null;
  altitude: number | null;
  producer: string | null;
  farm: string | null;
  region: string | null;
  tasting_notes: string[] | null;
  acidity: number | null;
  sweetness: number | null;
  body: number | null;
  created_at: string;
  updated_at: string;
}

export interface Cafe {
  id: string;
  name: string;
  location: string | null;
  address: string | null;
  website: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  updated_at: string;
  matching_beans: Bean[];
}
