import { useState } from "react";
import { uploadDocument } from "../api/client.js";

function FileUpload({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await uploadDocument(file);

      setFile(null);

      onUploadComplete?.();
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Failed to upload document."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <input
        type="file"
        accept="application/pdf"
        onChange={(event) =>
          setFile(event.target.files?.[0] || null)
        }
      />

      <button
        onClick={handleUpload}
        disabled={loading}
        className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
      >
        {loading ? "Uploading..." : "Upload PDF"}
      </button>

      {error && (
        <p className="text-sm text-red-500">
          {error}
        </p>
      )}
    </div>
  );
}

export default FileUpload;