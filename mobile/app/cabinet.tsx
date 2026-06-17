import { router, useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import {
  Alert,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { Button, Loader, Screen } from "@/components/ui";
import { colors, spacing } from "@/constants/theme";
import { fetchCabinet } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { CabinetChild } from "@/lib/types";

export default function CabinetScreen() {
  const { token, selectedChildId, parentName, children, signOut } = useAuth();
  const [tab, setTab] = useState<"child" | "parent">("child");
  const [data, setData] = useState<CabinetChild | null>(null);
  const [notifications, setNotifications] = useState<
    Array<{ message: string; date: string }>
  >([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!token || !selectedChildId) return;
    const resp = await fetchCabinet(token, selectedChildId);
    const child = resp.children[0] ?? null;
    setData(child);
    setNotifications(resp.notifications.slice(0, 5));
  }, [token, selectedChildId]);

  useFocusEffect(
    useCallback(() => {
      if (!token || !selectedChildId) {
        router.replace("/login");
        return;
      }
      setLoading(true);
      load()
        .catch((err) => Alert.alert("Ошибка", String(err)))
        .finally(() => setLoading(false));
    }, [token, selectedChildId, load]),
  );

  async function onRefresh() {
    setRefreshing(true);
    try {
      await load();
    } catch (err) {
      Alert.alert("Ошибка", String(err));
    } finally {
      setRefreshing(false);
    }
  }

  function openLesson(url?: string | null, slug?: string) {
    if (url) {
      router.push({ pathname: "/lesson", params: { url } });
      return;
    }
    if (slug) {
      router.push({ pathname: "/lesson", params: { slug } });
      return;
    }
    Alert.alert("Скоро", "Новое приключение откроется по расписанию модуля.");
  }

  if (loading && !data) return <Loader />;

  const cab = data?.cabinet;
  const childName = data?.name ?? "Ученик";

  return (
    <Screen>
      <View style={styles.tabs}>
        <Pressable
          onPress={() => setTab("child")}
          style={[styles.tab, tab === "child" && styles.tabActive]}
        >
          <Text style={[styles.tabText, tab === "child" && styles.tabTextActive]}>
            Комната
          </Text>
        </Pressable>
        <Pressable
          onPress={() => setTab("parent")}
          style={[styles.tab, tab === "parent" && styles.tabActive]}
        >
          <Text
            style={[styles.tabText, tab === "parent" && styles.tabTextActive]}
          >
            Родителям
          </Text>
        </Pressable>
      </View>

      <ScrollView
        style={{ flex: 1 }}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={{ gap: spacing.md, paddingBottom: spacing.xl }}
      >
        {tab === "child" ? (
          <>
            <View style={styles.hero}>
              <Text style={styles.greet}>Привет, {childName}!</Text>
              <Text style={styles.levelLine}>
                Уровень: <Text style={styles.strong}>{cab?.level}</Text>
              </Text>
              <Text style={styles.points}>{cab?.points ?? 0} Словиков</Text>
              {cab?.next_level_name ? (
                <Text style={styles.hint}>
                  До «{cab.next_level_name}» ещё {cab.points_to_next} Словиков
                </Text>
              ) : null}
              {cab?.companion?.hint ? (
                <Text style={styles.companion}>{cab.companion.hint}</Text>
              ) : null}
            </View>

            <Button
              label={
                cab?.continue_url
                  ? "Продолжить приключение"
                  : "Скоро новое приключение"
              }
              onPress={() => openLesson(cab?.continue_url)}
              disabled={!cab?.continue_url}
            />

            {data?.lessons?.length ? (
              <View style={styles.panel}>
                <Text style={styles.panelTitle}>Сказки</Text>
                {data.lessons.map((les) => (
                  <Pressable
                    key={les.slug}
                    style={styles.lessonRow}
                    onPress={() => openLesson(les.url, les.slug)}
                    disabled={!les.unlocked}
                  >
                    <Text style={styles.lessonTitle}>{les.title}</Text>
                    <Text style={styles.lessonMeta}>
                      {les.unlocked ? "Открыта" : "Закрыта"}
                    </Text>
                  </Pressable>
                ))}
              </View>
            ) : null}

            {cab?.chest ? (
              <View style={styles.panel}>
                <Text style={styles.panelTitle}>{cab.chest.title}</Text>
                <Text style={styles.hint}>{cab.chest.subtitle}</Text>
              </View>
            ) : null}
          </>
        ) : (
          <>
            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Здравствуйте, {parentName}</Text>
              {cab?.parent ? (
                Object.entries(cab.parent).map(([key, value]) => (
                  <Text key={key} style={styles.parentLine}>
                    {String(value)}
                  </Text>
                ))
              ) : (
                <Text style={styles.hint}>
                  Прогресс {childName}: {cab?.points ?? 0} Словиков, уровень «
                  {cab?.level}».
                </Text>
              )}
            </View>
            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Уведомления</Text>
              {notifications.length ? (
                notifications.map((n, i) => (
                  <Text key={i} style={styles.note}>
                    {n.date}
                    {"\n"}
                    {n.message.slice(0, 200)}
                  </Text>
                ))
              ) : (
                <Text style={styles.hint}>Пока нет сообщений.</Text>
              )}
            </View>
          </>
        )}

        {children.length > 1 ? (
          <Button
            label="Сменить ребёнка"
            variant="ghost"
            onPress={() => router.push("/pick-child")}
          />
        ) : null}
        <Button
          label="Выйти"
          variant="ghost"
          onPress={async () => {
            await signOut();
            router.replace("/login");
          }}
        />
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  tabs: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    backgroundColor: colors.bgSoft,
    alignItems: "center",
  },
  tabActive: {
    backgroundColor: colors.accentSoft,
    borderWidth: 1,
    borderColor: colors.accent,
  },
  tabText: { color: colors.textMuted, fontWeight: "600" },
  tabTextActive: { color: colors.accent },
  hero: {
    backgroundColor: colors.card,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: 6,
  },
  greet: { fontSize: 24, fontWeight: "700", color: colors.text },
  levelLine: { fontSize: 16, color: colors.text },
  strong: { fontWeight: "700" },
  points: { fontSize: 28, fontWeight: "800", color: colors.accent },
  hint: { color: colors.textMuted, lineHeight: 20 },
  companion: {
    marginTop: spacing.sm,
    color: colors.text,
    fontStyle: "italic",
  },
  panel: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.sm,
  },
  panelTitle: { fontSize: 18, fontWeight: "700", color: colors.text },
  lessonRow: {
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
  lessonTitle: { fontSize: 16, fontWeight: "600", color: colors.text },
  lessonMeta: { color: colors.textMuted, marginTop: 2 },
  parentLine: { color: colors.text, lineHeight: 22 },
  note: {
    color: colors.textMuted,
    lineHeight: 20,
    paddingBottom: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
});
