/**
 * Handles PDF document uploads.
 */

import { useState } from "react";

import { uploadDocument } from "../api/client.js";


function FileUpload({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");


  // -------------------------
  // 1. Select file
  // -------------------------

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setError("");

    if (!selectedFile) {
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setError("Only PDF files are allowed.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };


  // -------------------------
  // 2. Upload file
  // -------------------------

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF first.");
      return;
    }

    try {
      setUploading(true);
      setError("");

      await uploadDocument(file);

      setFile(null);

      onUploadComplete();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to upload document."
      );
    } finally {
      setUploading(false);
    }
  };


  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">

      {/* -------------------------
          3. Header
          ------------------------- */}

      <h2 className="text-sm font-semibold text-slate-800">
        Upload Document
      </h2>

      <p className="mt-1 text-xs text-slate-500">
        Upload a PDF to add it to your knowledge base.
      </p>


      {/* -------------------------
          4. File input
          ------------------------- */}

      <label className="mt-4 block cursor-pointer rounded-lg border-2 border-dashed border-slate-300 p-5 text-center transition hover:border-slate-500">

        <span className="text-2xl">
          📄
        </span>

        <p className="mt-2 text-sm font-medium text-slate-700">
          Choose a PDF
        </p>

        <p className="mt-1 text-xs text-slate-400">
          PDF files only
        </p>

        <input
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          className="hidden"
        />

      </label>


      {/* -------------------------
          5. Selected file
          ------------------------- */}

      {file && (
        <div className="mt-3 rounded-lg bg-slate-50 p-3">
          <p className="truncate text-sm text-slate-700">
            {file.name}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
      )}


      {/* -------------------------
          6. Upload button
          ------------------------- */}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="mt-4 w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {uploading ? "Uploading..." : "Upload PDF"}
      </button>


      {/* -------------------------
          7. Error
          ------------------------- */}

      {error && (
        <p className="mt-3 text-sm text-red-500">
          {error}
        </p>
      )}

    </div>
  );
}

export default FileUpload;