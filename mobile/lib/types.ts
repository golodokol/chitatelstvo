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

export type CabinetParentSummary = {
  completed_lessons: string;
  skill: string;
  points: string;
  chest_hint: string;
  chest_ready: string;
  support_tip: string;
  badges_count: string;
  current_lesson: string;
  level: string;
};

export type CabinetChest = {
  title?: string;
  subtitle?: string;
  hint?: string;
  reward?: string;
  tale_slug?: string;
  steps_total?: number;
  steps_done?: number;
  steps_remaining?: number;
  pct?: number;
  ready?: boolean;
  claimed?: boolean;
  visual?: string;
  image_url?: string;
  image_closed?: string;
  image_opening?: string;
  image_open?: string;
};

export type CabinetMission = {
  id: string;
  text: string;
  status: "done" | "active" | "locked";
};

export type CabinetBadge = {
  name: string;
  condition: string;
  earned: boolean;
  status: string;
  image?: string | null;
};

export type CabinetLevel = {
  name: string;
  status: string;
  sloviki_label: string;
  points_to_unlock: number;
  image?: string | null;
};

export type LessonLink = {
  slug: string;
  title: string;
  unlocked: boolean;
  url?: string;
  opens_on_label?: string;
  meeting_on_label?: string;
  week_in_stage?: number;
  ready?: boolean;
  cover_url?: string | null;
  cover_state?: string;
};

export type LessonStage = {
  key: string;
  label: string;
  lessons: LessonLink[];
};

export type ChildEvent = {
  type: string;
  type_label?: string;
  tale: string;
  date: string;
};

export type CabinetWeeklyLesson = {
  title?: string;
  goal?: string;
  duration?: string;
  url?: string;
  opens_on_label?: string;
  cover_url?: string | null;
  cover_state?: string;
  week_in_stage?: number;
  reward_pts?: number;
};

export type CabinetTrack = {
  group_code?: string;
  group_label?: string;
  module_title?: string;
  chest?: CabinetChest;
  weekly_lessons?: CabinetWeeklyLesson[];
  weekly_lessons_label?: string;
  missions?: CabinetMission[];
  missions_title?: string;
  missions_subtitle?: string | null;
};

export type CabinetChild = {
  id: string;
  name: string;
  level: string;
  points: number;
  badges?: string[];
  module_title?: string | null;
  has_meetings?: boolean;
  lessons?: LessonLink[];
  lesson_stages?: LessonStage[];
  events?: ChildEvent[];
  cabinet: {
    name: string;
    level: string;
    level_image?: string | null;
    points: number;
    points_label?: string;
    progress_pct: number;
    points_to_next?: number | null;
    next_level_name?: string | null;
    continue_url?: string | null;
    slovik_main_url?: string;
    slovik_preparing_url?: string;
    companion?: { url?: string; hint?: string; key?: string };
    chest?: CabinetChest;
    tracks?: CabinetTrack[];
    weekly_lessons?: CabinetWeeklyLesson[];
    weekly_lessons_label?: string;
    parent?: CabinetParentSummary;
    missions?: CabinetMission[];
    missions_title?: string;
    missions_subtitle?: string | null;
    badges?: CabinetBadge[];
    badges_earned_count?: number;
    badges_total?: number;
    levels?: CabinetLevel[];
    daily_lesson?: CabinetWeeklyLesson | null;
  };
};

export type ParentGuideStep = {
  label: string;
  note: string;
};

export type ParentGuidePoint = {
  label: string;
  value: string;
};

export type ParentGuide = {
  steps: ParentGuideStep[];
  points: ParentGuidePoint[];
};

export type CabinetResponse = {
  parent_name: string;
  email: string;
  module_start_date?: string | null;
  progress_url?: string;
  notification_channel?: string;
  parent_guide?: ParentGuide;
  telegram?: {
    enabled?: boolean;
    linked?: boolean;
    link_page?: string;
  };
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
