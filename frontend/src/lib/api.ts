// Centralized API client. Reads base URL from Vite env vars.
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface QueryResult {
  synthesized_answer: string;
  start_timestamp: number | null;
  end_timestamp: number | null;
}

export async function queryVideos(query: string): Promise<QueryResult> {
  const res = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || `Query failed (${res.status})`);
  }
  return res.json();
}