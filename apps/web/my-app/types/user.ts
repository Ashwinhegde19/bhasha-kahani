export interface User {
  id: string;
  anonymous_id: string;
  created_at: string;
  last_active: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  language: string;
  code_mix_ratio: number;
  volume: number;
  autoPlay: boolean;
}

export interface TokenResponse {
  access_token: string;
  expires_in: number;
  user_id: string;
}

export interface ChoiceRecord {
  node_id: string;
  choice_key: string;
  made_at: string;
}

export interface Progress {
  story_id: string;
  story_slug: string;
  story_title: string;
  cover_image: string;
  current_node_id?: string;
  is_completed: boolean;
  completion_percentage: number;
  play_count: number;
  total_time_sec: number;
  last_played_at?: string;
  choices_made: ChoiceRecord[];
}

export interface ProgressSummary {
  data: Progress[];
  summary: {
    total_stories_started: number;
    total_stories_completed: number;
    total_time_minutes: number;
  };
}

export interface ProgressUpdateRequest {
  story_id: string;
  current_node_id?: string;
  is_completed?: boolean;
  time_spent_sec?: number;
}

export interface Bookmark {
  id: string;
  story_id: string;
  story_slug: string;
  story_title: string;
  cover_image: string;
  notes?: string;
  created_at: string;
}
