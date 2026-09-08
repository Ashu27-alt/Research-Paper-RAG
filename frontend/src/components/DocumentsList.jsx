/**
 * Displays uploaded documents and allows deletion.
 */

import { useState } from "react";
import { deleteDocument } from "../api/client";

function DocumentList({ documents, onDocumentDeleted }) {
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");

  const handleDelete = async (documentId, filename) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(documentId);
      setError("");

      await deleteDocument(documentId);

      onDocumentDeleted(documentId);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to delete document."
      );
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="mt-6">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
        Documents
      </h2>

      {documents.length === 0 && (
        <p className="text-sm text-slate-400">
          No documents uploaded yet.
        </p>
      )}

      <div className="space-y-2">
        {documents.map((document) => {
          const deleting =
            deletingId === document.document_id;

          return (
            <div
              key={document.document_id}
              className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3"
            >
              <span className="text-lg">
                📄
              </span>

              <span className="min-w-0 flex-1 truncate text-sm font-medium text-slate-700">
                {document.filename}
              </span>

              <button
                type="button"
                onClick={() =>
                  handleDelete(
                    document.document_id,
                    document.filename
                  )
                }
                disabled={deleting}
                title="Delete document"
                className="rounded-md p-1.5 text-slate-400 transition hover:bg-red-50 hover:text-red-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {deleting ? "..." : "🗑️"}
              </button>
            </div>
          );
        })}
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-500">
          {error}
        </p>
      )}
    </div>
  );
}

export default DocumentList;