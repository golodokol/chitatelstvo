import { StyleSheet, Text, View } from "react-native";

import { RemoteImage, textNoBreak } from "@/components/RemoteImage";
import { colors, spacing } from "@/constants/theme";
import type { CabinetBadge } from "@/lib/types";

type BadgeGridProps = {
  badges: CabinetBadge[];
  earnedCount: number;
  total: number;
};

export function BadgeGrid({ badges, earnedCount, total }: BadgeGridProps) {
  const next = badges.find((b) => b.status === "next");

  return (
    <View style={styles.wrap}>
      <Text style={[styles.title, textNoBreak]}>
        Бейджи ({earnedCount} из {total})
      </Text>
      <View style={styles.grid}>
        {badges.map((badge) => (
          <View
            key={badge.name}
            style={[
              styles.item,
              badge.earned && styles.itemEarned,
              badge.status === "next" && styles.itemNext,
            ]}
          >
            <RemoteImage
              uri={badge.image}
              width={48}
              height={48}
              dimmed={!badge.earned && badge.status !== "next"}
            />
            <Text style={[styles.name, textNoBreak]}>{badge.name}</Text>
            {!badge.earned ? (
              <Text style={[styles.cond, textNoBreak]}>{badge.condition}</Text>
            ) : (
              <Text style={styles.earnedMark}>✓</Text>
            )}
          </View>
        ))}
      </View>
      {next ? (
        <Text style={[styles.nextHint, textNoBreak]}>
          Следующий: {next.name} — {next.condition}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: spacing.sm },
  title: { fontSize: 18, fontWeight: "700", color: colors.textWarm },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  item: {
    width: "31%",
    minWidth: 112,
    flexGrow: 1,
    alignItems: "center",
    padding: spacing.sm,
    borderRadius: 14,
    backgroundColor: colors.bgSoft,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 4,
  },
  itemEarned: {
    backgroundColor: colors.successBg,
    borderColor: colors.success,
  },
  itemNext: {
    borderColor: colors.accent,
    borderStyle: "dashed",
    backgroundColor: colors.accentSoft,
  },
  name: {
    fontSize: 11,
    fontWeight: "800",
    color: colors.text,
    textAlign: "center",
  },
  cond: { fontSize: 10, color: colors.textMuted, textAlign: "center" },
  earnedMark: { color: colors.success, fontWeight: "800", fontSize: 16 },
  nextHint: { color: colors.textMuted, lineHeight: 20 },
});
