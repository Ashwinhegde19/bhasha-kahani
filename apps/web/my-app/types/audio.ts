export interface AudioResponse {
  node_id: string;
  language: string;
  code_mix_ratio: number;
  speaker: string;
  audio_url: string;
  duration_sec?: number;
  file_size?: number;
  is_cached: boolean;
  expires_at?: string;
}

export interface AudioGeneratingResponse {
  node_id: string;
  language: string;
  code_mix_ratio: number;
  speaker: string;
  audio_url: string;
  status: 'generating';
  estimated_wait_sec: number;
  retry_after: number;
}

export interface AudioParams {
  language: string;
  speaker?: string;
  code_mix?: number;
}
