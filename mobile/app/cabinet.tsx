import { router, useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import {
  Alert,
  Linking,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { Button, Loader, Screen } from "@/components/ui";
import { BadgeGrid } from "@/components/BadgeGrid";
import { LessonHeroCard } from "@/components/LessonHeroCard";
import { LevelPath } from "@/components/LevelPath";
import { MissionChips } from "@/components/MissionChips";
import { RemoteImage, textNoBreak } from "@/components/RemoteImage";
import {
  LESSON_GUIDE_FOOTER,
  LESSON_GUIDE_INTRO,
  PARENT_INTRO,
} from "@/constants/cabinet-guide";
import { colors, spacing, API_BASE_URL } from "@/constants/theme";
import { claimChest, fetchCabinet, isAuthError } from "@/lib/api";
import {
  formatEventType,
  parentFacts,
} from "@/lib/cabinet-format";
import { useAuth } from "@/lib/auth-context";
import type { CabinetChest, CabinetResponse, CabinetTrack, LessonLink } from "@/lib/types";

function chestImageUrl(chest: CabinetChest): string | undefined {
  if (chest.claimed && chest.image_open) return chest.image_open;
  if (chest.ready && chest.image_opening) return chest.image_opening;
  return chest.image_url ?? chest.image_closed ?? undefined;
}

function lessonStatus(les: LessonLink): string {
  if (les.url) return "Открыта";
  if (les.unlocked && les.ready === false) return "Скоро появится";
  if (les.unlocked) return "Доступна";
  return "Закрыта";
}

export default function CabinetScreen() {
  const { token, selectedChildId, parentName, children, signOut } = useAuth();
  const [tab, setTab] = useState<"child" | "parent">("child");
  const [payload, setPayload] = useState<CabinetResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [claiming, setClaiming] = useState(false);

  const data = payload?.children[0] ?? null;
  const cab = data?.cabinet;
  const childName = data?.name ?? "Ученик";

  const load = useCallback(async () => {
    if (!token || !selectedChildId) return;
    const resp = await fetchCabinet(token, selectedChildId);
    setPayload(resp);
  }, [token, selectedChildId]);

  const handleLoadError = useCallback(
    async (err: unknown) => {
      if (isAuthError(err)) {
        await signOut();
        Alert.alert(
          "Нужно войти снова",
          "Сессия истекла. Запросите новый код на email.",
          [{ text: "OK", onPress: () => router.replace("/login") }],
        );
        return;
      }
      Alert.alert("Ошибка", String(err));
    },
    [signOut],
  );

  useFocusEffect(
    useCallback(() => {
      if (!token || !selectedChildId) {
        router.replace("/login");
        return;
      }
      setLoading(true);
      load()
        .catch(handleLoadError)
        .finally(() => setLoading(false));
    }, [token, selectedChildId, load, handleLoadError]),
  );

  async function onRefresh() {
    setRefreshing(true);
    try {
      await load();
    } catch (err) {
      await handleLoadError(err);
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

  async function onClaimChest(taleSlug: string) {
    if (!token || !selectedChildId || !taleSlug) return;
    setClaiming(true);
    try {
      const result = await claimChest(token, selectedChildId, taleSlug);
      if (result.status === "already_claimed") {
        Alert.alert("Сундук", "Награда уже получена.");
      } else {
        Alert.alert("Сундук", "Сундук открыт! Награда в сокровищнице.");
      }
      await load();
    } catch (err) {
      Alert.alert("Не удалось открыть сундук", String(err));
    } finally {
      setClaiming(false);
    }
  }

  if (loading && !data) return <Loader />;

  const stages = data?.lesson_stages?.length
    ? data.lesson_stages
    : data?.lessons?.length
      ? [{ key: "all", label: "Сказки", lessons: data.lessons }]
      : [];

  const courseTracks: CabinetTrack[] = cab?.tracks?.length
    ? cab.tracks
    : cab?.chest
      ? [
          {
            chest: cab.chest,
            weekly_lessons:
              cab.weekly_lessons ??
              (cab.daily_lesson ? [cab.daily_lesson] : []),
            weekly_lessons_label:
              cab.weekly_lessons_label ?? "Сказка этой недели",
            missions: cab.missions,
            missions_title: cab.missions_title,
            missions_subtitle: cab.missions_subtitle,
          },
        ]
      : [];

  return (
    <Screen>
      <View style={styles.brandRow}>
        <RemoteImage
          uri={`${API_BASE_URL}/assets/logo-chitatelstvo.png`}
          width={44}
          height={44}
        />
        <Text style={styles.brandTitle}>Читательство</Text>
      </View>
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
            {cab?.slovik_main_url ? (
              <View style={styles.slovikIntro}>
                <RemoteImage uri={cab.slovik_main_url} width={96} height={96} />
                <Text style={[styles.slovikText, textNoBreak]}>
                  Привет! Я — <Text style={styles.strong}>Словик</Text> ✨ Помогу собрать
                  Словики и открою сундук.
                </Text>
              </View>
            ) : null}

            <View style={styles.hero}>
              <View style={styles.heroTop}>
                <View style={styles.heroCopy}>
                  <Text style={styles.greet}>Привет, {childName}!</Text>
                  <Text style={styles.levelLine}>
                    Ты на уровне <Text style={styles.strong}>{cab?.level}</Text>
                  </Text>
                </View>
                {cab?.companion?.url ? (
                  <Pressable
                    style={({ pressed }) => [
                      styles.companionWrap,
                      (cab?.companion?.lesson_url ?? cab?.continue_url) &&
                        pressed &&
                        styles.companionWrapPressed,
                    ]}
                    onPress={() =>
                      openLesson(cab?.companion?.lesson_url ?? cab?.continue_url)
                    }
                    disabled={!(cab?.companion?.lesson_url ?? cab?.continue_url)}
                    accessibilityRole="button"
                    accessibilityLabel={
                      cab.companion.hint
                        ? `Перейти к уроку: ${cab.companion.hint}`
                        : "Словик"
                    }
                  >
                    <RemoteImage uri={cab.companion.url} width={80} height={80} />
                  </Pressable>
                ) : null}
              </View>

              <View style={styles.statsRow}>
                <View style={styles.stat}>
                  <RemoteImage uri={cab?.level_image} width={56} height={56} />
                  <Text style={styles.statLabel}>Уровень</Text>
                  <Text style={styles.statValue}>{cab?.level}</Text>
                </View>
                <View style={styles.stat}>
                  <RemoteImage
                    uri={cab?.slovik_preparing_url ?? cab?.companion?.url}
                    width={56}
                    height={56}
                  />
                  <Text style={styles.statLabel}>Словики</Text>
                  <Text style={[styles.statValue, styles.points]}>
                    {cab?.points ?? 0}
                  </Text>
                </View>
              </View>

              {cab?.progress_pct != null ? (
                <View style={styles.progressTrack}>
                  <View
                    style={[
                      styles.progressFill,
                      { width: `${Math.min(100, cab.progress_pct)}%` },
                    ]}
                  />
                </View>
              ) : null}
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

            {courseTracks.map((track, trackIndex) => (
              <View key={`${track.group_code ?? "track"}-${trackIndex}`}>
                {track.chest ? (
                  <View style={styles.panel}>
                    {track.group_label ? (
                      <Text style={styles.trackBadge}>{track.group_label}</Text>
                    ) : null}
                    <View style={styles.chestVisual}>
                      <RemoteImage
                        uri={chestImageUrl(track.chest)}
                        width={150}
                        height={150}
                      />
                      <Text style={styles.panelTitle}>{track.chest.title}</Text>
                      {track.chest.hint ? (
                        <Text style={styles.chestHint} numberOfLines={2}>
                          {track.chest.hint}
                        </Text>
                      ) : null}
                    </View>
                    {track.chest.steps_total ? (
                      <View style={styles.progressTrack}>
                        <View
                          style={[
                            styles.progressFill,
                            {
                              width: `${Math.min(
                                100,
                                ((track.chest.steps_done ?? 0) /
                                  track.chest.steps_total) *
                                  100,
                              )}%`,
                            },
                          ]}
                        />
                      </View>
                    ) : null}
                    {track.chest.steps_total ? (
                      <Text style={styles.hint}>
                        Искорки: {track.chest.steps_done ?? 0} / {track.chest.steps_total}
                      </Text>
                    ) : null}
                    {track.chest.ready && !track.chest.claimed && track.chest.tale_slug ? (
                      <Button
                        label={claiming ? "Открываем…" : "Открыть сундук"}
                        onPress={() => onClaimChest(track.chest!.tale_slug!)}
                        disabled={claiming}
                      />
                    ) : null}
                  </View>
                ) : null}

                {track.weekly_lessons?.length ? (
                  <View style={styles.panel}>
                    <Text style={styles.panelTitle}>
                      {track.weekly_lessons_label ?? "Сказка этой недели"}
                    </Text>
                    {track.group_label ? (
                      <Text style={styles.trackBadge}>{track.group_label}</Text>
                    ) : null}
                    <View style={styles.heroCards}>
                      {track.weekly_lessons.map((weekly, weeklyIndex) => (
                        <LessonHeroCard
                          key={`${weekly.title ?? "lesson"}-${weeklyIndex}`}
                          title={weekly.title}
                          coverUrl={weekly.cover_url}
                          meta={
                            weekly.opens_on_label
                              ? `Откроется ${weekly.opens_on_label}`
                              : undefined
                          }
                          active={Boolean(weekly.url)}
                          dimmed={!weekly.url}
                          onPress={
                            weekly.url ? () => openLesson(weekly.url) : undefined
                          }
                        />
                      ))}
                    </View>
                  </View>
                ) : null}

                {track.missions?.length ? (
                  <View style={styles.panel}>
                    <Text style={styles.panelTitle}>
                      {track.missions_title ?? "Миссии на эту неделю"}
                    </Text>
                    <MissionChips missions={track.missions} />
                  </View>
                ) : null}
              </View>
            ))}

            {stages.map((stage) => (
              <View key={stage.key} style={styles.panel}>
                <Text style={styles.panelTitle}>{stage.label}</Text>
                <View style={styles.heroCards}>
                  {stage.lessons.map((les) => (
                    <LessonHeroCard
                      key={les.slug}
                      compact
                      title={les.title}
                      coverUrl={les.cover_url}
                      meta={`${lessonStatus(les)}${
                        les.opens_on_label ? ` · ${les.opens_on_label}` : ""
                      }`}
                      active={Boolean(les.url)}
                      dimmed={!les.unlocked && !les.url}
                      onPress={() => openLesson(les.url, les.slug)}
                    />
                  ))}
                </View>
              </View>
            ))}

            {cab?.levels?.length ? (
              <View style={styles.panel}>
                <LevelPath levels={cab.levels} />
              </View>
            ) : null}

            {cab?.badges?.length ? (
              <View style={styles.panel}>
                <BadgeGrid
                  badges={cab.badges}
                  earnedCount={cab.badges_earned_count ?? 0}
                  total={cab.badges_total ?? cab.badges.length}
                />
              </View>
            ) : null}
          </>
        ) : (
          <>
            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Здравствуйте, {parentName}!</Text>
              <Text style={styles.hint}>{PARENT_INTRO}</Text>
            </View>

            {payload?.telegram?.enabled ? (
              <View style={styles.panel}>
                <Text style={styles.panelTitle}>Telegram</Text>
                {payload.telegram.linked ? (
                  <Text style={styles.hint}>
                    ✓ Telegram привязан — уведомления приходят в бот.
                  </Text>
                ) : payload.telegram.link_page ? (
                  <>
                    <Text style={styles.hint}>
                      Хотите дублировать уведомления в Telegram?
                    </Text>
                    <Button
                      label="Привязать Telegram"
                      variant="ghost"
                      onPress={() => Linking.openURL(payload.telegram!.link_page!)}
                    />
                  </>
                ) : (
                  <Text style={styles.hint}>
                    Уведомления доступны в приложении и по email.
                  </Text>
                )}
              </View>
            ) : null}

            <View style={styles.panel}>
              <View style={styles.parentChildHead}>
                {cab?.level_image ? (
                  <RemoteImage uri={cab.level_image} width={48} height={48} />
                ) : null}
                <Text style={styles.panelTitle}>{childName}</Text>
              </View>
              {cab?.parent ? (
                parentFacts(cab.parent, cab.next_level_name, cab.points_to_next).map(
                  (row) => (
                    <Text key={row.label} style={styles.factRow}>
                      <Text style={styles.factLabel}>{row.label}: </Text>
                      {row.value}
                    </Text>
                  ),
                )
              ) : null}
              {data?.badges?.length ? (
                <Text style={styles.factRow}>
                  <Text style={styles.factLabel}>Полученные бейджи: </Text>
                  {data.badges.join(", ")}
                </Text>
              ) : null}
              {data?.module_title ? (
                <Text style={styles.factRow}>
                  <Text style={styles.factLabel}>Модуль: </Text>
                  {data.module_title}
                </Text>
              ) : null}
              {cab?.parent?.support_tip ? (
                <Text style={styles.tip}>{cab.parent.support_tip}</Text>
              ) : null}
            </View>

            {data?.events?.length ? (
              <View style={styles.panel}>
                <Text style={styles.panelTitle}>Недавние занятия</Text>
                {data.events.slice(0, 8).map((e, i) => (
                  <Text key={i} style={styles.note}>
                    {e.date} — {e.type_label ?? formatEventType(e.type)}
                    {e.tale !== "—" ? ` («${e.tale}»)` : ""}
                  </Text>
                ))}
              </View>
            ) : null}

            {stages.length ? (
              <View style={styles.panel}>
                <Text style={styles.panelTitle}>
                  {data?.schedule_intro?.heading ?? "Расписание сказок"}
                </Text>
                <Text style={styles.hint}>
                  {data?.schedule_intro?.text
                    ? data.schedule_intro.text
                    : payload?.module_start_date
                      ? `Первый этап начинается ${payload.module_start_date} — новая сказка по понедельникам.`
                      : "Даты открытия указаны у каждого урока ниже."}
                </Text>
                {stages.map((stage) => (
                  <View key={stage.key} style={styles.stageBlock}>
                    <Text style={styles.stageTitle}>{stage.label}</Text>
                    {stage.lessons.map((les) => (
                      <View key={les.slug} style={styles.scheduleRow}>
                        <Text style={styles.lessonTitle}>{les.title}</Text>
                        <Text style={styles.lessonMeta}>
                          Сказка {les.week_in_stage ?? "—"}
                          {les.opens_on_label
                            ? ` · ${les.url ? "с" : "откроется"} ${les.opens_on_label}`
                            : ""}
                          {les.meeting_on_label
                            ? ` · встреча ${les.meeting_on_label}`
                            : ""}
                        </Text>
                      </View>
                    ))}
                  </View>
                ))}
              </View>
            ) : null}

            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Как проходит урок</Text>
              <Text style={styles.hint}>{LESSON_GUIDE_INTRO}</Text>
              {(payload?.parent_guide?.steps ?? []).map((step, i) => (
                <Text key={step.label} style={styles.guideStep}>
                  {i + 1}. {step.label} — {step.note}
                </Text>
              ))}
              <Text style={styles.hint}>{LESSON_GUIDE_FOOTER}</Text>
            </View>

            <View style={styles.panel}>
              <Text style={styles.panelTitle}>За что начисляются Словики</Text>
              {(payload?.parent_guide?.points ?? []).map((row) => (
                <View key={row.label} style={styles.pointsRow}>
                  <Text style={styles.pointsAction}>{row.label}</Text>
                  <Text style={styles.pointsValue}>{row.value}</Text>
                </View>
              ))}
            </View>

            <View style={styles.panel}>
              <Text style={styles.panelTitle}>Лента уведомлений</Text>
              {payload?.notifications?.length ? (
                payload.notifications.map((n, i) => (
                  <Text key={i} style={styles.note}>
                    {n.date} · {n.channel}
                    {"\n"}
                    {n.message}
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
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  brandTitle: { fontSize: 18, fontWeight: "700", color: colors.text },
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
    backgroundColor: colors.bluePale,
    borderWidth: 1,
    borderColor: colors.blue,
  },
  tabText: { color: colors.textMuted, fontWeight: "600" },
  tabTextActive: { color: colors.blue },
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
  points: { fontSize: 24, fontWeight: "800", color: colors.blue },
  slovikIntro: {
    flexDirection: "row",
    gap: spacing.md,
    alignItems: "center",
    backgroundColor: colors.bluePale,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  slovikText: { flex: 1, color: colors.text, lineHeight: 22, fontSize: 15 },
  heroTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: spacing.sm,
  },
  heroCopy: { flex: 1, gap: 4 },
  companionWrap: {
    backgroundColor: colors.bgSoft,
    borderRadius: 16,
    padding: 4,
  },
  companionWrapPressed: {
    opacity: 0.85,
    transform: [{ scale: 0.97 }],
  },
  statsRow: {
    flexDirection: "row",
    gap: spacing.md,
    marginTop: spacing.md,
  },
  stat: {
    flex: 1,
    alignItems: "center",
    gap: 4,
    backgroundColor: colors.bgSoft,
    borderRadius: 14,
    padding: spacing.sm,
  },
  statLabel: { fontSize: 12, color: colors.textMuted, fontWeight: "600" },
  statValue: { fontSize: 16, fontWeight: "700", color: colors.text, textAlign: "center" },
  heroCards: { gap: spacing.md },
  trackBadge: {
    alignSelf: "flex-start",
    backgroundColor: colors.accentSoft,
    color: colors.accent,
    fontSize: 13,
    fontWeight: "700",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    overflow: "hidden",
  },
  chestVisual: {
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.sm,
  },
  progressTrack: {
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.bgSoft,
    marginTop: spacing.sm,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.blue,
    borderRadius: 4,
  },
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
  panelTitle: { fontSize: 18, fontWeight: "700", color: colors.textWarm },
  scheduleRow: {
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
  lessonTitle: { fontSize: 16, fontWeight: "600", color: colors.text },
  lessonMeta: { color: colors.textMuted, marginTop: 2, lineHeight: 18 },
  chestHint: { color: colors.blue, fontWeight: "600", textAlign: "center" },
  factRow: { color: colors.text, lineHeight: 22 },
  parentChildHead: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  factLabel: { fontWeight: "700" },
  tip: {
    marginTop: spacing.sm,
    color: colors.text,
    lineHeight: 22,
    fontStyle: "italic",
  },
  stageBlock: { gap: 4, marginTop: spacing.sm },
  stageTitle: { fontWeight: "700", color: colors.text, marginBottom: 4 },
  guideStep: { color: colors.text, lineHeight: 22 },
  pointsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: spacing.sm,
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
  pointsAction: { flex: 1, color: colors.text, lineHeight: 20 },
  pointsValue: { color: colors.blue, fontWeight: "700" },
  note: {
    color: colors.textMuted,
    lineHeight: 20,
    paddingBottom: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
});
