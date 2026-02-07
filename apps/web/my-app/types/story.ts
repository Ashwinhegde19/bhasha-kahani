export interface Character {
  id: string;
  slug: string;
  name: string;
  voice_profile: string;
  bulbul_speaker: string;
  avatar_url?: string;
}

export interface Choice {
  id: string;
  choice_key: string;
  text: string;
  next_node_id?: string;
}

export interface StoryNode {
  id: string;
  node_type: 'narration' | 'dialogue' | 'choice' | 'end';
  display_order: number;
  is_start: boolean;
  is_end: boolean;
  text: string;
  character?: Character;
  choices?: Choice[];
}

export interface Story {
  id: string;
  slug: string;
  title: string;
  description: string;
  language: string;
  age_range: string;
  region: string;
  moral?: string;
  duration_min: number;
  cover_image: string;
  character_count: number;
  choice_count: number;
  is_completed_translation: boolean;
  created_at: string;
}

export interface StoryDetail extends Story {
  available_languages: string[];
  characters: Character[];
  nodes: StoryNode[];
  start_node_id: string;
  updated_at: string;
}

export interface StoryFilters {
  language?: string;
  age_range?: string;
  region?: string;
  search?: string;
  page?: number;
  limit?: number;
}

export interface StoryListResponse {
  data: Story[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface MakeChoiceRequest {
  node_id: string;
  choice_key: string;
}

export interface MakeChoiceResponse {
  success: boolean;
  choice_made: {
    node_id: string;
    choice_key: string;
    choice_text: string;
  };
  next_node: StoryNode;
  progress: {
    completion_percentage: number;
    choices_made_count: number;
  };
}
