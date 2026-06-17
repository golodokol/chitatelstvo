import * as SecureStore from "expo-secure-store";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { AuthChild } from "@/lib/types";

const TOKEN_KEY = "chit_access_token";
const CHILD_KEY = "chit_selected_child_id";
const CHILDREN_KEY = "chit_children_json";
const PARENT_KEY = "chit_parent_name";
const EMAIL_KEY = "chit_email";

type AuthState = {
  ready: boolean;
  token: string | null;
  email: string | null;
  parentName: string | null;
  children: AuthChild[];
  selectedChildId: string | null;
};

type AuthContextValue = AuthState & {
  signIn: (payload: {
    token: string;
    email: string;
    parentName: string;
    children: AuthChild[];
  }) => Promise<void>;
  selectChild: (childId: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    ready: false,
    token: null,
    email: null,
    parentName: null,
    children: [],
    selectedChildId: null,
  });

  useEffect(() => {
    (async () => {
      const [token, selectedChildId, childrenJson, parentName, email] =
        await Promise.all([
          SecureStore.getItemAsync(TOKEN_KEY),
          SecureStore.getItemAsync(CHILD_KEY),
          SecureStore.getItemAsync(CHILDREN_KEY),
          SecureStore.getItemAsync(PARENT_KEY),
          SecureStore.getItemAsync(EMAIL_KEY),
        ]);
      setState({
        ready: true,
        token,
        email,
        parentName,
        selectedChildId,
        children: childrenJson ? JSON.parse(childrenJson) : [],
      });
    })();
  }, []);

  const signIn = useCallback(
    async (payload: {
      token: string;
      email: string;
      parentName: string;
      children: AuthChild[];
    }) => {
      await Promise.all([
        SecureStore.setItemAsync(TOKEN_KEY, payload.token),
        SecureStore.setItemAsync(EMAIL_KEY, payload.email),
        SecureStore.setItemAsync(PARENT_KEY, payload.parentName),
        SecureStore.setItemAsync(
          CHILDREN_KEY,
          JSON.stringify(payload.children),
        ),
      ]);
      const autoChild =
        payload.children.length === 1 ? payload.children[0].id : null;
      if (autoChild) {
        await SecureStore.setItemAsync(CHILD_KEY, autoChild);
      } else {
        await SecureStore.deleteItemAsync(CHILD_KEY);
      }
      setState((prev) => ({
        ...prev,
        token: payload.token,
        email: payload.email,
        parentName: payload.parentName,
        children: payload.children,
        selectedChildId: autoChild,
      }));
    },
    [],
  );

  const selectChild = useCallback(async (childId: string) => {
    await SecureStore.setItemAsync(CHILD_KEY, childId);
    setState((prev) => ({ ...prev, selectedChildId: childId }));
  }, []);

  const signOut = useCallback(async () => {
    await Promise.all([
      SecureStore.deleteItemAsync(TOKEN_KEY),
      SecureStore.deleteItemAsync(CHILD_KEY),
      SecureStore.deleteItemAsync(CHILDREN_KEY),
      SecureStore.deleteItemAsync(PARENT_KEY),
      SecureStore.deleteItemAsync(EMAIL_KEY),
    ]);
    setState({
      ready: true,
      token: null,
      email: null,
      parentName: null,
      children: [],
      selectedChildId: null,
    });
  }, []);

  const value = useMemo(
    () => ({ ...state, signIn, selectChild, signOut }),
    [state, signIn, selectChild, signOut],
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside AuthProvider");
  return ctx;
}
