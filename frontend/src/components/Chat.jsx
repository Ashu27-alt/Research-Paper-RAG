/**
 * Chat interface for asking questions across all uploaded documents.
 */

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { askQuestion } from "../api/client.js";
import SourceCard from "./SourceCard.jsx";

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const messagesEndRef = useRef(null);

  // -------------------------
  // Auto-scroll
  // -------------------------

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // -------------------------
  // Submit question
  // -------------------------

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setError("");

    // -------------------------
    // 1. Add user message
    // -------------------------

    setMessages((previous) => [
      ...previous,
      {
        type: "user",
        content: trimmedQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      // -------------------------
      // 2. Ask backend
      // -------------------------

      const response = await askQuestion({
        question: trimmedQuestion,
        topK: 5,
        maxDistance: 1.0,
      });

      // -------------------------
      // 3. Add assistant message
      // -------------------------

      setMessages((previous) => [
        ...previous,
        {
          type: "assistant",
          content: response.answer,
          sources: response.sources || [],
        },
      ]);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to get an answer."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-slate-200 pb-5">
        <h2 className="text-lg font-semibold text-slate-900">
          Document Chat
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Ask questions across all uploaded documents.
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 space-y-6 overflow-y-auto py-6">
        {/* Empty state */}
        {messages.length === 0 && !loading && (
          <div className="flex h-full items-center justify-center">
            <div className="max-w-md text-center">
              <div className="text-4xl">
                💬
              </div>

              <h3 className="mt-4 text-base font-semibold text-slate-800">
                Ask your documents anything
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Ask a question and get a grounded answer
                using information from all uploaded documents.
              </p>
            </div>
          </div>
        )}

        {/* Conversation */}
        {messages.map((message, index) => (
          <div
            key={index}
            className={
              message.type === "user"
                ? "flex justify-end"
                : "flex justify-start"
            }
          >
            {message.type === "user" ? (
              <div className="max-w-2xl rounded-2xl rounded-br-md bg-slate-900 px-4 py-3 text-sm text-white">
                {message.content}
              </div>
            ) : (
              <div className="max-w-3xl">
                {/* Markdown answer */}
                <div className="rounded-2xl rounded-bl-md border border-slate-200 bg-white px-5 py-4 text-sm leading-6 text-slate-700 shadow-sm">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => (
                        <h1 className="mb-3 text-xl font-bold text-slate-900">
                          {children}
                        </h1>
                      ),

                      h2: ({ children }) => (
                        <h2 className="mb-2 mt-4 text-lg font-semibold text-slate-900">
                          {children}
                        </h2>
                      ),

                      h3: ({ children }) => (
                        <h3 className="mb-2 mt-3 text-base font-semibold text-slate-900">
                          {children}
                        </h3>
                      ),

                      p: ({ children }) => (
                        <p className="mb-3 last:mb-0">
                          {children}
                        </p>
                      ),

                      ul: ({ children }) => (
                        <ul className="mb-3 list-disc space-y-1 pl-5">
                          {children}
                        </ul>
                      ),

                      ol: ({ children }) => (
                        <ol className="mb-3 list-decimal space-y-1 pl-5">
                          {children}
                        </ol>
                      ),

                      li: ({ children }) => (
                        <li>{children}</li>
                      ),

                      strong: ({ children }) => (
                        <strong className="font-semibold text-slate-900">
                          {children}
                        </strong>
                      ),

                      blockquote: ({ children }) => (
                        <blockquote className="my-3 border-l-4 border-slate-300 pl-4 italic text-slate-500">
                          {children}
                        </blockquote>
                      ),

                      code: ({ children }) => (
                        <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-800">
                          {children}
                        </code>
                      ),

                      pre: ({ children }) => (
                        <pre className="my-3 overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs leading-5 text-slate-100">
                          {children}
                        </pre>
                      ),

                      a: ({ children, href }) => (
                        <a
                          href={href}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-slate-900 underline"
                        >
                          {children}
                        </a>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>

                {/* Sources */}
                {message.sources?.length > 0 && (
                  <div className="mt-3">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Sources
                    </p>

                    <div className="grid gap-2 sm:grid-cols-2">
                      {message.sources.map((source) => (
                        <SourceCard
                          key={`${source.chunk_id}-${source.source}`}
                          source={source}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Loading */}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-md border border-slate-200 bg-white px-5 py-4 shadow-sm">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />

                <span
                  className="h-2 w-2 animate-bounce rounded-full bg-slate-400"
                  style={{
                    animationDelay: "100ms",
                  }}
                />

                <span
                  className="h-2 w-2 animate-bounce rounded-full bg-slate-400"
                  style={{
                    animationDelay: "200ms",
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Scroll target */}
        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="mb-3 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-slate-200 pt-4"
      >
        <div className="flex items-end gap-3">
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                handleSubmit(event);
              }
            }}
            placeholder="Ask a question about your documents..."
            rows={2}
            disabled={loading}
            className="min-h-[52px] flex-1 resize-none rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200 disabled:bg-slate-50"
          />

          <button
            type="submit"
            disabled={!question.trim() || loading}
            className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? "..." : "Ask"}
          </button>
        </div>

        <p className="mt-2 text-xs text-slate-400">
          Press Enter to send · Shift + Enter for a new line
        </p>
      </form>
    </div>
  );
}

export default Chat;