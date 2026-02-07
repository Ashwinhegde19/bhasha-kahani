export const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
  { code: 'bn', name: 'বাংলা', flag: '🇧🇩' },
  { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
  { code: 'kn', name: 'ಕನ್ನಡ', flag: '🇮🇳' },
] as const;

export const AGE_RANGES = [
  { value: '4-6', label: 'Ages 4-6' },
  { value: '7-10', label: 'Ages 7-10' },
  { value: '11-14', label: 'Ages 11-14' },
] as const;

export const REGIONS = [
  { value: 'pan-indian', label: 'Pan-Indian' },
  { value: 'bengali', label: 'Bengali' },
  { value: 'tamil', label: 'Tamil' },
  { value: 'hindi', label: 'Hindi' },
] as const;

export const SPEAKERS = [
  { id: 'meera', name: 'Meera', gender: 'female', style: 'warm_elderly' },
  { id: 'arvind', name: 'Arvind', gender: 'male', style: 'young_energetic' },
] as const;
