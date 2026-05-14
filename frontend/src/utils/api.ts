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

// File Selection API Methods
export async function getDiscoveredFiles(websiteId: number, page: number = 1, pageSize: number = 20) {
  const response = await apiFetch(`/api/v1/websites/${websiteId}/files?page=${page}&page_size=${pageSize}`);
  return response.json();
}

export async function searchFiles(websiteId: number, query: string) {
  const response = await apiFetch(`/api/v1/websites/${websiteId}/files/search?q=${encodeURIComponent(query)}`);
  return response.json();
}

export async function selectFiles(websiteId: number, fileIds: number[]) {
  const response = await apiFetch(`/api/v1/websites/${websiteId}/files/select`, {
    method: 'POST',
    body: JSON.stringify({ file_ids: fileIds })
  });
  return response.json();
}

export async function deselectFiles(websiteId: number, fileIds: number[]) {
  const response = await apiFetch(`/api/v1/websites/${websiteId}/files/deselect`, {
    method: 'POST',
    body: JSON.stringify({ file_ids: fileIds })
  });
  return response.json();
}

export async function getFilePreview(fileId: number) {
  const response = await apiFetch(`/api/v1/websites/files/${fileId}/preview`);
  return response.json();
}

export async function triggerIngestion(websiteId: number, fileIds?: number[]) {
  const response = await apiFetch(`/api/v1/websites/${websiteId}/ingestion/trigger`, {
    method: 'POST',
    body: JSON.stringify(fileIds ? { file_ids: fileIds } : {})
  });
  return response.json();
}

export async function getIngestionJobStatus(jobId: number) {
  const response = await apiFetch(`/api/v1/ingestion/jobs/${jobId}/status`);
  return response.json();
}

export async function getWebsites() {
  const response = await apiFetch('/api/v1/websites');
  return response.json();
}

export async function getWebsiteDetail(websiteId: number) {
  const response = await apiFetch(`/api/v1/websites/${websiteId}`);
  return response.json();
}
