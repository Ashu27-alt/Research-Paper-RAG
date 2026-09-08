/**
 * API client for communicating with the FastAPI backend.
 */

import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000",
});

// -------------------------
// Document APIs
// -------------------------

export const getDocuments = async () => {
  const response = await apiClient.get("/documents");
  return response.data;
};

export const uploadDocument = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await apiClient.post(
    "/upload",
    formData
  );

  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await apiClient.delete(
    `/documents/${documentId}`
  );

  return response.data;
};

// -------------------------
// Chat API
// -------------------------

export const askQuestion = async ({
  question,
  documentId = null,
  topK = 5,
  maxDistance = 1.0,
}) => {
  const payload = {
    question,
    top_k: topK,
    max_distance: maxDistance,
  };

  if (documentId) {
    payload.document_id = documentId;
  }

  const response = await apiClient.post(
    "/chat",
    payload
  );

  return response.data;
};

export default apiClient;