import { API_BASE_URL } from "@/constants/theme";
import type {
  AuthChild,
  CabinetResponse,
  LessonResponse,
  OtpVerifyResponse,
} from "@/lib/types";

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function parseJson<T>(resp: Response): Promise<T> {
  const text = await resp.text();
  let data: unknown = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  if (!resp.ok) {
    const detail =
      typeof data === "object" && data && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : `Ошибка ${resp.status}`;
    throw new ApiError(resp.status, detail);
  }
  return data as T;
}

export async function requestOtp(email: string): Promise<void> {
  const resp = await fetch(`${API_BASE_URL}/api/v1/auth/otp/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email.trim().toLowerCase() }),
  });
  await parseJson(resp);
}

export async function verifyOtp(
  email: string,
  code: string,
): Promise<OtpVerifyResponse> {
  const resp = await fetch(`${API_BASE_URL}/api/v1/auth/otp/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email.trim().toLowerCase(),
      code: code.trim(),
    }),
  });
  return parseJson<OtpVerifyResponse>(resp);
}

export async function fetchCabinet(
  token: string,
  childId: string,
): Promise<CabinetResponse> {
  const url = `${API_BASE_URL}/api/v1/cabinet?child_id=${encodeURIComponent(childId)}`;
  const resp = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseJson<CabinetResponse>(resp);
}

export async function claimChest(
  token: string,
  childId: string,
  taleSlug: string,
): Promise<{ status: string }> {
  const resp = await fetch(`${API_BASE_URL}/api/v1/chest/claim`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ child_id: childId, tale_slug: taleSlug }),
  });
  return parseJson(resp);
}

export async function fetchLesson(
  token: string,
  childId: string,
  slug: string,
  testKey?: string,
): Promise<LessonResponse> {
  const qs = new URLSearchParams({ child_id: childId });
  if (testKey) qs.set("test_key", testKey);
  const resp = await fetch(
    `${API_BASE_URL}/api/v1/lessons/${encodeURIComponent(slug)}?${qs}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  return parseJson<LessonResponse>(resp);
}

export { ApiError };
export type { AuthChild };
