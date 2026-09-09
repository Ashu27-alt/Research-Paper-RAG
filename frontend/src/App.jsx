import { useState } from "react";

import FileUpload from "./components/FileUpload.jsx";
import DocumentList from "./components/DocumentsList.jsx";
import Chat from "./components/Chat.jsx";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadComplete = () => {
    setRefreshKey((value) => value + 1);
  };

  return (
    <div className="min-h-screen p-6">
      <div className="mx-auto max-w-6xl space-y-8">

        <h1 className="text-3xl font-bold">
          RAG Document Intelligence
        </h1>

        <section>
          <h2 className="mb-4 text-xl font-semibold">
            Upload Document
          </h2>

          <FileUpload
            onUploadComplete={handleUploadComplete}
          />
        </section>

        <section>
          <h2 className="mb-4 text-xl font-semibold">
            Documents
          </h2>

          <DocumentList
            refreshKey={refreshKey}
          />
        </section>

        <section>
          <h2 className="mb-4 text-xl font-semibold">
            Ask Questions
          </h2>

          <Chat />
        </section>

      </div>
    </div>
  );
}

export default App;