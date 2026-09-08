/**
 * Main application layout.
 */

import { useEffect, useState } from "react";
import { getDocuments } from "./api/client";
import DocumentList from "./components/DocumentsList.jsx";
import FileUpload from "./components/FileUpload.jsx";
import Chat from "./components/Chat.jsx";

function App() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // -------------------------
  // Load documents
  // -------------------------

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDocuments();

      setDocuments(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to load documents."
      );
    } finally {
      setLoading(false);
    }
  };

  // -------------------------
  // Remove deleted document
  // -------------------------

  const handleDocumentDeleted = (documentId) => {
    setDocuments((previous) =>
      previous.filter(
        (document) =>
          document.document_id !== documentId
      )
    );
  };

  // -------------------------
  // Initial load
  // -------------------------

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              RAG Document Intelligence
            </h1>

            <p className="mt-1 text-xs text-slate-500">
              Search and chat across your documents
            </p>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-6 py-6 lg:grid-cols-[320px_1fr]">
        {/* Sidebar */}
        <aside className="space-y-6">
          {/* Upload */}
          <FileUpload
            onUploadComplete={loadDocuments}
          />

          {/* Documents */}
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <DocumentList
              documents={documents}
              onDocumentDeleted={
                handleDocumentDeleted
              }
            />
          </div>
        </aside>

        {/* Chat */}
        <section className="min-h-[calc(100vh-140px)] rounded-xl border border-slate-200 bg-white p-6">
          <Chat />
        </section>
      </main>

      {/* Global error */}
      {error && (
        <div className="fixed bottom-5 right-5 max-w-sm rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 shadow-lg">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="fixed bottom-5 left-5 rounded-lg bg-white px-4 py-3 text-sm text-slate-500 shadow-lg">
          Loading documents...
        </div>
      )}
    </div>
  );
}

export default App;