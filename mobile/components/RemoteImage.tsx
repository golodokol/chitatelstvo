import { Image, Platform, StyleSheet, View, type ImageStyle, type ViewStyle } from "react-native";

import { colors } from "@/constants/theme";
import { resolveMediaUrl } from "@/lib/media-url";

type RemoteImageProps = {
  uri?: string | null;
  width: number;
  height?: number;
  style?: ImageStyle;
  containerStyle?: ViewStyle;
  rounded?: boolean;
  dimmed?: boolean;
};

export function RemoteImage({
  uri,
  width,
  height,
  style,
  containerStyle,
  rounded,
  dimmed,
}: RemoteImageProps) {
  const resolved = resolveMediaUrl(uri);
  const h = height ?? width;

  if (!resolved) {
    return (
      <View
        style={[
          { width, height: h, backgroundColor: colors.bgSoft },
          rounded ? styles.rounded : undefined,
          containerStyle,
        ]}
      />
    );
  }

  return (
    <View
      style={[
        rounded ? styles.rounded : undefined,
        dimmed ? styles.dimmed : undefined,
        containerStyle,
      ]}
    >
      <Image
        source={{ uri: resolved }}
        style={[{ width, height: h }, style]}
        resizeMode="contain"
        accessibilityIgnoresInvertColors
      />
    </View>
  );
}

/** Стили текста без разрыва слов посередине (RU). */
export const textNoBreak = {
  ...(Platform.OS === "android"
    ? { textBreakStrategy: "simple" as const, includeFontPadding: false }
    : {}),
  ...(Platform.OS === "ios" ? { lineBreakStrategyIOS: "push-out" as const } : {}),
};

const styles = StyleSheet.create({
  rounded: {
    borderRadius: 12,
    overflow: "hidden",
    backgroundColor: colors.bgSoft,
  },
  dimmed: { opacity: 0.45 },
});
