import { useEffect, useState } from "react";
import {
  getDocuments,
  deleteDocument,
} from "../api/client";

function DocumentList({ refreshKey }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshKey]);

  useEffect(() => {
    const hasProcessingDocuments = documents.some(
      (document) =>
        document.processing_status === "pending" ||
        document.processing_status === "processing"
    );

    if (!hasProcessingDocuments) {
      return;
    }

    const interval = setInterval(() => {
      fetchDocuments();
    }, 2000);

    return () => clearInterval(interval);
  }, [documents]);

  const handleDelete = async (documentId) => {
    try {
      await deleteDocument(documentId);
      await fetchDocuments();
    } catch (error) {
      console.error("Failed to delete document:", error);
    }
  };

  if (loading) {
    return <p>Loading documents...</p>;
  }

  return (
    <div className="space-y-3">
      {documents.length === 0 ? (
        <p className="text-gray-500">
          No documents uploaded yet.
        </p>
      ) : (
        documents.map((document) => (
          <div
            key={document.document_id}
            className="flex items-center justify-between rounded-lg border p-4"
          >
            <div>
              <p className="font-medium">
                {document.filename}
              </p>

              <p className="text-sm text-gray-500">
                {document.processing_status}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <StatusBadge
                status={document.processing_status}
              />

              <button
                onClick={() =>
                  handleDelete(document.document_id)
                }
                className="rounded bg-red-500 px-3 py-1 text-sm text-white hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function StatusBadge({ status }) {
  const statusConfig = {
    pending: {
      label: "Pending",
    },
    processing: {
      label: "Processing...",
    },
    completed: {
      label: "Completed",
    },
    failed: {
      label: "Failed",
    },
  };

  const config = statusConfig[status] || {
    label: status,
  };

  return (
    <span className="rounded-full border px-3 py-1 text-xs">
      {config.label}
    </span>
  );
}

export default DocumentList;