import Constants from "expo-constants";

export const API_BASE_URL =
  (Constants.expoConfig?.extra?.apiBaseUrl as string | undefined) ??
  "https://api.chitatelstvo.ru";

/** Палитра как в static/chit-student.css (веб-кабинет) */
export const colors = {
  bg: "#F6F4F9",
  bgSoft: "#EFEBF5",
  bgDeep: "#E8F1F8",
  border: "#D4E2EF",
  text: "#3D5266",
  textWarm: "#3A4553",
  textMuted: "#6B8499",
  blue: "#5B7FA6",
  blueLight: "#88A9D1",
  bluePale: "#E8F1F8",
  accent: "#8F7DA3",
  accentSoft: "#EBE6F3",
  card: "#FFFFFF",
  success: "#2E7D32",
  successBg: "#E8F5E9",
  danger: "#B44A3A",
};

export const spacing = {
  xs: 6,
  sm: 10,
  md: 16,
  lg: 24,
  xl: 32,
};
