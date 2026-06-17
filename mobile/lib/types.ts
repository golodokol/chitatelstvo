export type AuthChild = {
  id: string;
  name: string;
  age?: number | null;
  level: string;
  points: number;
  family_id: string;
};

export type OtpVerifyResponse = {
  access_token: string;
  expires_in: number;
  family_id: string;
  parent_name: string;
  progress_url: string;
  children: AuthChild[];
};

export type CabinetChild = {
  id: string;
  name: string;
  level: string;
  points: number;
  module_title?: string | null;
  cabinet: {
    name: string;
    level: string;
    points: number;
    progress_pct: number;
    points_to_next?: number | null;
    next_level_name?: string | null;
    continue_url?: string | null;
    companion?: { url?: string; hint?: string };
    chest?: {
      title?: string;
      subtitle?: string;
      ready?: boolean;
      claimed?: boolean;
      tale_slug?: string;
    };
    parent?: Record<string, string | number>;
  };
  lessons?: Array<{
    slug: string;
    title: string;
    unlocked: boolean;
    url?: string;
  }>;
};

export type CabinetResponse = {
  parent_name: string;
  email: string;
  children: CabinetChild[];
  notifications: Array<{ message: string; date: string; channel: string }>;
};

export type LessonResponse = {
  slug: string;
  title: string;
  lesson_url: string;
  video: { type?: string; url?: string; id?: string };
  comprehension_quiz?: unknown;
};
