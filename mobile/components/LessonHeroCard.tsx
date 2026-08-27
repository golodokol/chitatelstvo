import { Pressable, StyleSheet, Text, useWindowDimensions, View } from "react-native";

import { RemoteImage } from "@/components/RemoteImage";
import { colors, spacing } from "@/constants/theme";

type LessonHeroCardProps = {
  title?: string;
  coverUrl?: string | null;
  meta?: string;
  actionLabel?: string;
  onPress?: () => void;
  disabled?: boolean;
  dimmed?: boolean;
  active?: boolean;
  compact?: boolean;
};

export function LessonHeroCard({
  title,
  coverUrl,
  meta,
  actionLabel = "Начать урок",
  onPress,
  disabled,
  dimmed,
  active,
  compact,
}: LessonHeroCardProps) {
  const { width: screenW } = useWindowDimensions();
  const cardW = screenW - spacing.lg * 2 - spacing.md * 2;
  const canOpen = Boolean(active && onPress && !disabled);

  return (
    <Pressable
      style={({ pressed }) => [
        styles.card,
        canOpen ? styles.cardActive : undefined,
        pressed && canOpen ? styles.cardPressed : undefined,
      ]}
      onPress={canOpen ? onPress : undefined}
      disabled={!canOpen}
    >
      <RemoteImage
        uri={coverUrl}
        width={cardW}
        rounded
        dimmed={dimmed}
        autoAspect
        containerStyle={styles.coverWrap}
      />
      <View style={styles.body}>
        {title ? (
          <Text style={[styles.title, compact && styles.titleCompact]} numberOfLines={2}>
            {title}
          </Text>
        ) : null}
        {canOpen ? (
          <View style={styles.cta}>
            <Text style={styles.ctaText}>{actionLabel}</Text>
          </View>
        ) : (
          <Text style={styles.meta}>{meta ?? "Скоро откроется"}</Text>
        )}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 18,
    overflow: "hidden",
    backgroundColor: colors.bgSoft,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardActive: {
    borderColor: colors.blueLight,
    backgroundColor: colors.bluePale,
  },
  cardPressed: {
    opacity: 0.92,
    transform: [{ scale: 0.99 }],
  },
  coverWrap: {
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
    backgroundColor: colors.accentSoft,
    alignSelf: "center",
  },
  body: {
    padding: spacing.sm,
    gap: spacing.xs,
  },
  title: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.textWarm,
    lineHeight: 24,
  },
  titleCompact: {
    fontSize: 16,
  },
  meta: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.textMuted,
    textAlign: "center",
    paddingVertical: spacing.xs,
  },
  cta: {
    backgroundColor: colors.blue,
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 4,
  },
  ctaText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
  },
});
