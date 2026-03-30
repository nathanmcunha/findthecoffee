export interface Roaster {
  id: string;
  name: string;
  website?: string | null;
  location?: string | null;
  address?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface Bean {
  id: string;
  name: string;
  roaster_name: string | null;
  roast_level: string | null;
  origin: string | null;
}

export interface Cafe {
  id: string;
  name: string;
  location: string | null;
  address?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  website?: string | null;
  matching_beans: Bean[];
}
