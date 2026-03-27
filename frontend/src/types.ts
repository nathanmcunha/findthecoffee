export interface Roaster {
  id: number;
  name: string;
}

export interface Bean {
  id: number;
  name: string;
  roaster_name: string | null;
  tasting_notes: string[] | null;
  variety: string | null;
  processing: string | null;
  altitude: number | null;
  roast_level: string | null;
  acidity: number | null;
  sweetness: number | null;
  body: number | null;
}

export interface Cafe {
  id: number;
  name: string;
  location: string | null;
  matching_beans: Bean[];
}
