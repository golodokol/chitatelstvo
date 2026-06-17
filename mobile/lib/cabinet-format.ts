import type { CabinetParentSummary } from "@/lib/types";

const EVENT_LABELS: Record<string, string> = {
  lesson_complete: "Просмотр видео",
  comprehension: "Квиз «Понимание»",
  meaning_analysis: "Квиз «Смысл»",
  creative_task: "Творческое задание",
  retelling: "Пересказ",
  live_meeting: "Живая встреча",
};

export function formatEventType(type: string): string {
  return EVENT_LABELS[type] ?? type;
}

export function parentFacts(
  parent: CabinetParentSummary,
  nextLevel?: string | null,
  pointsToNext?: number | null,
): Array<{ label: string; value: string }> {
  const rows: Array<{ label: string; value: string }> = [
    { label: "Уровень", value: parent.level },
    { label: "Словиков", value: parent.points },
    { label: "Бейджей", value: parent.badges_count },
    { label: "Пройдено уроков", value: parent.completed_lessons },
    { label: "Сейчас развивается", value: parent.skill },
    { label: "Текущий урок", value: parent.current_lesson },
    { label: "Сундук", value: parent.chest_ready },
  ];
  if (nextLevel && pointsToNext != null) {
    rows.push({
      label: "До следующего уровня",
      value: `${pointsToNext} Словиков («${nextLevel}»)`,
    });
  }
  return rows;
}

export function missionStatusLabel(status: string): string {
  if (status === "done") return "Готово";
  if (status === "active") return "Сейчас";
  return "Скоро";
}
