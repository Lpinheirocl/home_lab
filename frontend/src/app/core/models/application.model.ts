export interface Application {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  icon: string | null;
  category: string | null;
  namespace: string | null;
  access_url: string | null;
  favorite: boolean;
  visible: boolean;
  discovery_source: string;
  created_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  name: string;
  display_name: string;
  description?: string;
  icon?: string;
  category?: string;
  namespace?: string;
  access_url?: string;
  favorite: boolean;
  visible: boolean;
  discovery_source?: string;
  resources?: {resource_type: string; resource_name: string; namespace: string}[];
}

export interface ApplicationUpdate {
  display_name?: string;
  description?: string;
  icon?: string;
  category?: string;
  namespace?: string;
  access_url?: string;
  favorite?: boolean;
  visible?: boolean;
}
