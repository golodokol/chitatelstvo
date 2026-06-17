import Constants from "expo-constants";

export const API_BASE_URL =
  (Constants.expoConfig?.extra?.apiBaseUrl as string | undefined) ??
  "https://api.chitatelstvo.ru";

export const colors = {
  bg: "#fffcf7",
  bgSoft: "#f9f2e8",
  bgDeep: "#f0e6d6",
  border: "#dcc9a8",
  text: "#3d2f24",
  textMuted: "#7a6654",
  accent: "#2f6b4f",
  accentSoft: "#e8f3ec",
  card: "#fffdf9",
  danger: "#b44a3a",
};

export const spacing = {
  xs: 6,
  sm: 10,
  md: 16,
  lg: 24,
  xl: 32,
};
