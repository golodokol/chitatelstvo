import { ScrollView, StyleSheet, Text, View } from "react-native";

import { RemoteImage, textNoBreak } from "@/components/RemoteImage";
import { colors, spacing } from "@/constants/theme";
import type { CabinetLevel } from "@/lib/types";

const STATUS_LABEL: Record<string, string> = {
  done: "пройден",
  current: "сейчас",
  next: "следующий",
  locked: "впереди",
};

type LevelPathProps = {
  levels: CabinetLevel[];
};

export function LevelPath({ levels }: LevelPathProps) {
  if (!levels.length) return null;

  return (
    <View style={styles.wrap}>
      <Text style={[styles.title, textNoBreak]}>Путь героя</Text>
      <Text style={[styles.sub, textNoBreak]}>
        Словики открывают новые ступени — от Старта до Литературного детектива
      </Text>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.row}
      >
        {levels.map((lvl) => (
          <View
            key={lvl.name}
            style={[
              styles.step,
              lvl.status === "current" && styles.stepCurrent,
              lvl.status === "done" && styles.stepDone,
              lvl.status === "locked" && styles.stepLocked,
            ]}
          >
            <RemoteImage
              uri={lvl.image}
              width={56}
              height={56}
              dimmed={lvl.status === "locked"}
            />
            <Text style={[styles.stepName, textNoBreak]}>{lvl.name}</Text>
            <Text style={[styles.stepPts, textNoBreak]}>{lvl.sloviki_label}</Text>
            <Text style={[styles.stepStatus, textNoBreak]}>
              {STATUS_LABEL[lvl.status] ?? lvl.status}
            </Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: spacing.sm },
  title: { fontSize: 18, fontWeight: "700", color: colors.textWarm },
  sub: { color: colors.textMuted, lineHeight: 20 },
  row: { gap: spacing.sm, paddingVertical: spacing.xs },
  step: {
    width: 118,
    alignItems: "center",
    gap: 4,
    padding: spacing.sm,
    borderRadius: 14,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
  },
  stepCurrent: {
    backgroundColor: colors.bluePale,
    borderColor: colors.blue,
  },
  stepDone: {
    backgroundColor: colors.successBg,
    borderColor: colors.success,
  },
  stepLocked: { opacity: 0.55 },
  stepName: {
    fontSize: 11,
    fontWeight: "800",
    color: colors.text,
    textAlign: "center",
  },
  stepPts: { fontSize: 10, color: colors.textMuted, textAlign: "center" },
  stepStatus: { fontSize: 10, color: colors.blue, fontWeight: "600" },
});
