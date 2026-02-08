import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  Story, 
  StoryDetail, 
  StoryFilters, 
  StoryListResponse, 
  MakeChoiceRequest, 
  MakeChoiceResponse,
  AudioResponse,
  AudioParams,
  TokenResponse,
  ProgressSummary,
  ProgressUpdateRequest
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken();
          // Optionally redirect to login or refresh token
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  // Auth API
  async anonymousAuth(): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/anonymous');
    return response.data;
  }

  // Stories API
  async listStories(filters: StoryFilters = {}): Promise<StoryListResponse> {
    const response = await this.client.get<StoryListResponse>('/stories', {
      params: filters,
    });
    return response.data;
  }

  async getStory(slug: string, language?: string): Promise<StoryDetail> {
    const response = await this.client.get<StoryDetail>(`/stories/${slug}`, {
      params: { language },
    });
    return response.data;
  }

  // Audio API
  async getAudioUrl(nodeId: string, params: AudioParams): Promise<AudioResponse> {
    const response = await this.client.get<AudioResponse>(`/audio/${nodeId}`, {
      params,
    });
    return response.data;
  }

  // Choices API
  async makeChoice(
    storySlug: string, 
    data: MakeChoiceRequest
  ): Promise<MakeChoiceResponse> {
    // TODO: Backend path should be /stories/{slug}/choices but currently at /choices/{slug}/choices
    const response = await this.client.post<MakeChoiceResponse>(
      `/choices/${storySlug}/choices`,
      data
    );
    return response.data;
  }

  // User Progress API
  async getUserProgress(userId: string): Promise<ProgressSummary> {
    const response = await this.client.get<ProgressSummary>('/users/progress', {
      params: { user_id: userId },
    });
    return response.data;
  }

  async updateProgress(data: ProgressUpdateRequest): Promise<{ success: boolean }> {
    // Backend expects query parameters, not JSON body
    const response = await this.client.post<{ success: boolean }>('/users/progress', null, {
      params: {
        user_id: data.user_id,
        story_id: data.story_id,
        current_node_id: data.current_node_id,
        is_completed: data.is_completed ?? false,
        time_spent_sec: data.time_spent_sec ?? 0,
      },
    });
    return response.data;
  }
}

export const api = new ApiClient();
