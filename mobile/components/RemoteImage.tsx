import { useEffect, useState } from "react";
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
  resizeMode?: "contain" | "cover";
  /** Высота по пропорциям картинки (width задаёт ширину, без обрезки). */
  autoAspect?: boolean;
};

export function RemoteImage({
  uri,
  width,
  height,
  style,
  containerStyle,
  rounded,
  dimmed,
  resizeMode = "contain",
  autoAspect,
}: RemoteImageProps) {
  const resolved = resolveMediaUrl(uri);
  const fallbackH = height ?? width;
  const [aspectHeight, setAspectHeight] = useState(fallbackH);

  useEffect(() => {
    if (!autoAspect || !resolved) {
      setAspectHeight(fallbackH);
      return;
    }
    let cancelled = false;
    Image.getSize(
      resolved,
      (imgW, imgH) => {
        if (cancelled || imgW <= 0) return;
        setAspectHeight(Math.round(width * (imgH / imgW)));
      },
      () => {
        if (!cancelled) setAspectHeight(fallbackH);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [autoAspect, resolved, width, fallbackH]);

  const h = autoAspect ? aspectHeight : fallbackH;
  const mode = autoAspect ? "contain" : resizeMode;

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
        { width, height: h, overflow: "hidden" },
        rounded ? styles.rounded : undefined,
        dimmed ? styles.dimmed : undefined,
        containerStyle,
      ]}
    >
      <Image
        source={{ uri: resolved }}
        style={[{ width, height: h }, style]}
        resizeMode={mode}
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
