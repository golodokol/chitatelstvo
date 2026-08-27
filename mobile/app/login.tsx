import { router } from "expo-router";
import { useState } from "react";
import { Alert, Text } from "react-native";

import { Button, Field, Screen } from "@/components/ui";
import { requestOtp } from "@/lib/api";

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    const value = email.trim().toLowerCase();
    if (!value.includes("@")) {
      Alert.alert("Проверьте email", "Введите адрес, который указали при записи.");
      return;
    }
    setLoading(true);
    try {
      const resp = await requestOtp(value);
      router.push({
        pathname: "/verify",
        params: { email: value, hint: resp.message },
      });
    } catch (err) {
      Alert.alert("Не удалось отправить код", String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen
      title="Читательство"
      subtitle="Введите email, который указали при записи ребёнка. Мы пришлём код для входа."
    >
      <Field
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="email-address"
        placeholder="email@example.com"
        value={email}
        onChangeText={setEmail}
        editable={!loading}
      />
      <Button
        label={loading ? "Отправляем…" : "Получить код"}
        onPress={onSubmit}
        disabled={loading}
      />
      <Text style={{ color: "#7a6654", fontSize: 14, lineHeight: 20 }}>
        Код приходит только на email из формы записи на chitatelstvo.ru — тот же,
        что в письме «Добро пожаловать». Проверьте «Спам» и папку «Промоакции».
      </Text>
    </Screen>
  );
}
