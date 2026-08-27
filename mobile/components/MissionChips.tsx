import { StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "@/constants/theme";
import { missionStatusLabel } from "@/lib/cabinet-format";
import type { CabinetMission } from "@/lib/types";

export function MissionChips({ missions }: { missions: CabinetMission[] }) {
  return (
    <View style={styles.wrap}>
      {missions.map((m) => {
        const done = m.status === "done";
        const locked = m.status === "locked";
        return (
          <View
            key={m.id}
            style={[
              styles.chip,
              done && styles.chipDone,
              locked && styles.chipLocked,
            ]}
          >
            <Text style={styles.chipIcon}>{done ? "✓" : locked ? "○" : "★"}</Text>
            <Text style={styles.chipText} numberOfLines={2}>
              {m.text}
            </Text>
            <Text
              style={[
                styles.chipStatus,
                done && styles.chipStatusDone,
                locked && styles.chipStatusLocked,
              ]}
            >
              {missionStatusLabel(m.status)}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  chip: {
    width: "48%",
    minWidth: 140,
    flexGrow: 1,
    backgroundColor: colors.bluePale,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
    gap: 4,
  },
  chipDone: {
    backgroundColor: colors.successBg,
    borderColor: "#C8E6C9",
  },
  chipLocked: {
    backgroundColor: colors.bgSoft,
    opacity: 0.85,
  },
  chipIcon: {
    fontSize: 16,
    color: colors.blue,
    fontWeight: "700",
  },
  chipText: {
    fontSize: 13,
    fontWeight: "600",
    color: colors.text,
    lineHeight: 18,
  },
  chipStatus: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.blue,
  },
  chipStatusDone: {
    color: colors.success,
  },
  chipStatusLocked: {
    color: colors.textMuted,
  },
});
