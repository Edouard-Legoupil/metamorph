// utils/api.ts
export async function apiFetch(path: string, options: any = {}) {
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem("API_KEY") : null;
  options.headers = {
    ...(options.headers || {}),
    "X-API-Key": apiKey || "",
    "Content-Type": options.headers?.["Content-Type"] || "application/json"
  };
  const resp = await fetch(path, options);
  // Handle unauthorized
  if (resp.status === 401 && typeof window !== 'undefined') {
    localStorage.removeItem('API_KEY');
    window.location.href = '/login';
    return;
  }
  return resp;
}
