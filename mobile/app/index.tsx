import { Redirect } from "expo-router";

import { Loader } from "@/components/ui";
import { useAuth } from "@/lib/auth-context";

export default function Index() {
  const { ready, token, selectedChildId, children } = useAuth();

  if (!ready) return <Loader />;

  if (!token) return <Redirect href="/login" />;

  if (!selectedChildId) {
    if (children.length > 1) return <Redirect href="/pick-child" />;
    if (children.length === 1) return <Redirect href="/cabinet" />;
    return <Redirect href="/login" />;
  }

  return <Redirect href="/cabinet" />;
}
