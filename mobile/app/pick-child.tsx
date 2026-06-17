import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { Button, Screen } from "@/components/ui";
import { colors, spacing } from "@/constants/theme";
import { useAuth } from "@/lib/auth-context";

export default function PickChildScreen() {
  const { children, selectChild } = useAuth();

  async function choose(id: string) {
    await selectChild(id);
    router.replace("/cabinet");
  }

  return (
    <Screen
      title="Кто занимается?"
      subtitle="Выберите ребёнка — откроется его комната приключений."
    >
      <View style={styles.list}>
        {children.map((child) => (
          <Pressable
            key={child.id}
            style={({ pressed }) => [
              styles.card,
              pressed && { opacity: 0.9 },
            ]}
            onPress={() => choose(child.id)}
          >
            <Text style={styles.name}>{child.name}</Text>
            <Text style={styles.meta}>
              {child.level} · {child.points} Словиков
            </Text>
          </Pressable>
        ))}
      </View>
      <Button label="Назад" variant="ghost" onPress={() => router.back()} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: { gap: spacing.sm },
  card: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  name: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.text,
  },
  meta: {
    marginTop: 4,
    color: colors.textMuted,
    fontSize: 15,
  },
});
