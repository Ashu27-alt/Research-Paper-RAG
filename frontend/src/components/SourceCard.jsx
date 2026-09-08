/**
 * Displays metadata for a source used to generate an answer.
 */

function SourceCard({ source }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">

      {/* -------------------------
          1. Source header
          ------------------------- */}

      <div className="flex items-center justify-between">

        <span className="text-xs font-semibold text-slate-700">
          {source.source}
        </span>

        <span className="rounded-md bg-white px-2 py-1 text-xs text-slate-500">
          Page {source.page_number}
        </span>

      </div>


      {/* -------------------------
          2. Document
          ------------------------- */}

      <p className="mt-2 truncate text-sm font-medium text-slate-800">
        {source.filename}
      </p>


      {/* -------------------------
          3. Chunk information
          ------------------------- */}

      <p className="mt-1 text-xs text-slate-500">
        Chunk {source.chunk_id}
      </p>

    </div>
  );
}

export default SourceCard;