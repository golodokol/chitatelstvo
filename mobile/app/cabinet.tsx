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
import { LevelPath } from "@/components/LevelPath";
import { RemoteImage, textNoBreak } from "@/components/RemoteImage";
import {
  LESSON_GUIDE_FOOTER,
  LESSON_GUIDE_INTRO,
  LESSON_GUIDE_STEPS,
  PARENT_INTRO,
  POINTS_RULES,
} from "@/constants/cabinet-guide";
import { colors, spacing, API_BASE_URL } from "@/constants/theme";
import { claimChest, fetchCabinet } from "@/lib/api";
import {
  formatEventType,
  missionStatusLabel,
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
              cab.weekly_lessons_label ?? "Урок этой недели",
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
                <RemoteImage uri={cab.slovik_main_url} width={80} height={80} />
                <Text style={[styles.slovikText, textNoBreak]}>
                  Привет! Я — <Text style={styles.strong}>Словик</Text> ✨ Буду рядом в
                  приключениях: подскажу про сундук и помогу собрать Словики за каждое
                  занятие.
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
                  <View style={styles.companionWrap}>
                    <RemoteImage uri={cab.companion.url} width={80} height={80} />
                  </View>
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
                      <Text style={styles.hint}>{track.group_label}</Text>
                    ) : null}
                    <View style={styles.chestHeader}>
                      <RemoteImage
                        uri={chestImageUrl(track.chest)}
                        width={120}
                        height={120}
                      />
                      <View style={styles.chestCopy}>
                        <Text style={styles.panelTitle}>{track.chest.title}</Text>
                        <Text style={styles.hint}>{track.chest.subtitle}</Text>
                      </View>
                    </View>
                    {track.chest.hint ? (
                      <Text style={styles.chestHint}>{track.chest.hint}</Text>
                    ) : null}
                    {track.chest.steps_total ? (
                      <Text style={styles.hint}>
                        Шагов: {track.chest.steps_done ?? 0} из {track.chest.steps_total}
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
                      {track.weekly_lessons_label ?? "Урок этой недели"}
                    </Text>
                    {track.group_label ? (
                      <Text style={styles.hint}>{track.group_label}</Text>
                    ) : null}
                    {track.weekly_lessons.map((weekly, weeklyIndex) => (
                      <View key={`${weekly.title ?? "lesson"}-${weeklyIndex}`} style={styles.lessonCard}>
                        <RemoteImage
                          uri={weekly.cover_url}
                          width={64}
                          height={88}
                          rounded
                          dimmed={!weekly.url}
                        />
                        <View style={styles.lessonCardBody}>
                          <Text style={styles.lessonTitle}>{weekly.title}</Text>
                          {weekly.goal ? (
                            <Text style={styles.hint}>{weekly.goal}</Text>
                          ) : null}
                          {weekly.opens_on_label && !weekly.url ? (
                            <Text style={styles.hint}>
                              Откроется: {weekly.opens_on_label}
                            </Text>
                          ) : null}
                          {weekly.url ? (
                            <Button
                              label="Начать урок"
                              variant="ghost"
                              onPress={() => openLesson(weekly.url)}
                            />
                          ) : null}
                        </View>
                      </View>
                    ))}
                  </View>
                ) : null}

                {track.missions?.length ? (
                  <View style={styles.panel}>
                    <Text style={styles.panelTitle}>
                      {track.missions_title ?? "Миссии на эту неделю"}
                    </Text>
                    {track.missions_subtitle ? (
                      <Text style={styles.hint}>
                        {track.group_label ? `${track.group_label} · ` : ""}
                        {track.missions_subtitle}
                      </Text>
                    ) : null}
                    {track.missions.map((m) => (
                      <View key={`${trackIndex}-${m.id}`} style={styles.missionRow}>
                        <Text style={styles.missionText}>{m.text}</Text>
                        <Text style={styles.missionStatus}>
                          {missionStatusLabel(m.status)}
                        </Text>
                      </View>
                    ))}
                  </View>
                ) : null}
              </View>
            ))}

            {stages.map((stage) => (
              <View key={stage.key} style={styles.panel}>
                <Text style={styles.panelTitle}>{stage.label}</Text>
                {stage.lessons.map((les) => (
                  <Pressable
                    key={les.slug}
                    style={styles.lessonRow}
                    onPress={() => openLesson(les.url, les.slug)}
                    disabled={!les.url && !les.unlocked}
                  >
                    <View style={styles.lessonCard}>
                      <RemoteImage
                        uri={les.cover_url}
                        width={52}
                        height={72}
                        rounded
                        dimmed={!les.unlocked && !les.url}
                      />
                      <View style={styles.lessonCardBody}>
                        <Text style={styles.lessonTitle}>{les.title}</Text>
                        <Text style={styles.lessonMeta}>
                          {lessonStatus(les)}
                          {les.opens_on_label ? ` · ${les.opens_on_label}` : ""}
                        </Text>
                      </View>
                    </View>
                  </Pressable>
                ))}
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
                    {e.date} — {formatEventType(e.type)}
                    {e.tale !== "—" ? ` («${e.tale}»)` : ""}
                  </Text>
                ))}
              </View>
            ) : null}

            {stages.length ? (
              <View style={styles.panel}>
                <Text style={styles.panelTitle}>Расписание сказок</Text>
                <Text style={styles.hint}>
                  {payload?.module_start_date
                    ? `Первый этап начинается ${payload.module_start_date} — новая сказка по понедельникам.`
                    : "Новая сказка открывается раз в неделю по понедельникам."}
                  {data?.has_meetings
                    ? " Встречи с преподавателем — по четвергам."
                    : ""}
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
              {LESSON_GUIDE_STEPS.map((step, i) => (
                <Text key={step.title} style={styles.guideStep}>
                  {i + 1}. {step.title} — {step.points}
                </Text>
              ))}
              <Text style={styles.hint}>{LESSON_GUIDE_FOOTER}</Text>
            </View>

            <View style={styles.panel}>
              <Text style={styles.panelTitle}>За что начисляются Словики</Text>
              {POINTS_RULES.map((row) => (
                <View key={row.action} style={styles.pointsRow}>
                  <Text style={styles.pointsAction}>{row.action}</Text>
                  <Text style={styles.pointsValue}>{row.points}</Text>
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
  lessonCard: {
    flexDirection: "row",
    gap: spacing.sm,
    alignItems: "flex-start",
  },
  lessonCardBody: { flex: 1, gap: 4 },
  chestHeader: {
    flexDirection: "row",
    gap: spacing.md,
    alignItems: "center",
  },
  chestCopy: { flex: 1, gap: 4 },
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
  lessonRow: {
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
  scheduleRow: {
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
  lessonTitle: { fontSize: 16, fontWeight: "600", color: colors.text },
  lessonMeta: { color: colors.textMuted, marginTop: 2, lineHeight: 18 },
  missionRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: spacing.sm,
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: colors.bgSoft,
  },
  missionText: { flex: 1, color: colors.text, lineHeight: 20 },
  missionStatus: { color: colors.blue, fontWeight: "600", fontSize: 13 },
  chestHint: { color: colors.blue, fontWeight: "600" },
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
