import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import { Alert, Text } from "react-native";

import { Button, Field, Screen } from "@/components/ui";
import { verifyOtp } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function VerifyScreen() {
  const { email: emailParam, hint: hintParam } = useLocalSearchParams<{
    email?: string;
    hint?: string;
  }>();
  const email = String(emailParam || "");
  const hint = String(hintParam || "");
  const { signIn } = useAuth();
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    if (code.trim().length < 4) {
      Alert.alert("Введите код", "6 цифр из письма.");
      return;
    }
    setLoading(true);
    try {
      const data = await verifyOtp(email, code);
      await signIn({
        token: data.access_token,
        email,
        parentName: data.parent_name,
        children: data.children,
      });
      if (data.children.length > 1) {
        router.replace("/pick-child");
      } else {
        router.replace("/cabinet");
      }
    } catch (err) {
      Alert.alert("Неверный код", String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen
      title="Код из письма"
      subtitle={
        hint ||
        `Если ${email} был в форме записи, код уже отправлен. Проверьте почту и «Спам».`
      }
    >
      <Field
        keyboardType="number-pad"
        placeholder="123456"
        value={code}
        onChangeText={setCode}
        maxLength={8}
        editable={!loading}
      />
      <Button
        label={loading ? "Проверяем…" : "Войти"}
        onPress={onSubmit}
        disabled={loading}
      />
      <Button
        label="Другой email"
        variant="ghost"
        onPress={() => router.replace("/login")}
      />
      <Text style={{ color: "#7a6654", fontSize: 14, lineHeight: 20 }}>
        Письма нет? Убедитесь, что email совпадает с записью на сайте. Другой
        адрес — код не отправляется (это нормально). Ищите тему «Код для входа
        в Читательство» от school@yandex.ru.
      </Text>
    </Screen>
  );
}
