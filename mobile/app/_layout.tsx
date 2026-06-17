import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

import { AuthProvider } from "@/lib/auth-context";
import { colors } from "@/constants/theme";

export default function RootLayout() {
  return (
    <AuthProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
          headerShadowVisible: false,
          contentStyle: { backgroundColor: colors.bg },
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="login" options={{ title: "Вход" }} />
        <Stack.Screen name="verify" options={{ title: "Код из письма" }} />
        <Stack.Screen name="pick-child" options={{ title: "Кто занимается?" }} />
        <Stack.Screen name="cabinet" options={{ title: "Комната приключений" }} />
        <Stack.Screen name="lesson" options={{ title: "Урок" }} />
      </Stack>
    </AuthProvider>
  );
}
