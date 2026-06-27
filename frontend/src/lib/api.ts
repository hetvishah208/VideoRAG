// Centralized API client. Reads base URL + key from Vite env vars so no
// secrets are hardcoded in components. See frontend/.env.example.
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY ?? "";

function headers(): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
  };
}

export interface QueryResult {
  synthesized_answer: string;
  start_timestamp: number | null;
  end_timestamp: number | null;
}

export async function queryVideos(query: string): Promise<QueryResult> {
  const res = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    throw new Error(`Query failed (${res.status})`);
  }
  return res.json();
}
