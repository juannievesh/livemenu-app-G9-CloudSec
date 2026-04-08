const API_BASE = "https://livemenu-backend-403658009429.us-central1.run.app";
const API_PREFIX = '/api/v1';

function getToken(): string | null {
  return localStorage.getItem('token');
}

export async function fetchApi<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const url = `${API_BASE}${API_PREFIX}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: { ...headers, ...(options.headers as Record<string, string>) },
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    const msg = (err as { detail?: string | string[] }).detail;
    const text = Array.isArray(msg) ? msg.join(', ') : msg || response.statusText;
    throw new Error(text || 'API Error');
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

export async function fetchBlob(endpoint: string): Promise<Blob> {
  const token = getToken();
  const url = `${API_BASE}${API_PREFIX}${endpoint}`;
  const res = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  if (!res.ok) throw new Error('Failed to fetch');
  return res.blob();
}
