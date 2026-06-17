import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { Alert, StyleSheet, View } from "react-native";
import { WebView } from "react-native-webview";

import { Loader } from "@/components/ui";
import { fetchLesson } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { colors } from "@/constants/theme";

export default function LessonScreen() {
  const { url: urlParam, slug: slugParam } = useLocalSearchParams<{
    url?: string;
    slug?: string;
  }>();
  const { token, selectedChildId } = useAuth();
  const [lessonUrl, setLessonUrl] = useState<string | null>(
    urlParam ? String(urlParam) : null,
  );
  const [loading, setLoading] = useState(!urlParam && !!slugParam);

  useEffect(() => {
    if (urlParam || !slugParam || !token || !selectedChildId) return;
    (async () => {
      try {
        const data = await fetchLesson(
          token,
          selectedChildId,
          String(slugParam),
        );
        setLessonUrl(data.lesson_url);
      } catch (err) {
        Alert.alert("Урок недоступен", String(err), [
          { text: "Назад", onPress: () => router.back() },
        ]);
      } finally {
        setLoading(false);
      }
    })();
  }, [urlParam, slugParam, token, selectedChildId]);

  if (loading || !lessonUrl) return <Loader />;

  return (
    <View style={styles.wrap}>
      <WebView
        source={{ uri: lessonUrl }}
        startInLoadingState
        allowsInlineMediaPlayback
        mediaPlaybackRequiresUserAction={false}
        onError={() =>
          Alert.alert("Ошибка", "Не удалось загрузить урок.", [
            { text: "Назад", onPress: () => router.back() },
          ])
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
});
