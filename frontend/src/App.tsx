import { useState, useRef } from "react";
import VideoUpload from "./components/VideoUpload";
import QueryInput from "./components/QueryInput";
import AnswerDisplay from "./components/AnswerDisplay";

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

function App() {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [answerTimestamp, setAnswerTimestamp] = useState<number | null>(null);

  const previewVideoRef = useRef<HTMLVideoElement | null>(null);
  const answerVideoRef = useRef<HTMLVideoElement | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-64 bg-gray-300 p-4 shadow-lg">
          <h1 className="text-2xl font-bold mb-6">VideoRAG</h1>
          <VideoUpload
            setVideoUrl={(url) => {
              setVideoUrl(url);
              setAnswer("");
              setError(null);
              setAnswerTimestamp(null);
            }}
            setError={setError}
          />
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8 bg-gradient-to-br from-blue-50 via-white to-purple-50 rounded-lg shadow-xl">
          <h1 className="text-3xl font-bold mb-4 text-center">Ask a question</h1>

          {videoUrl && (
            <div className="mb-6 flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-2">Main Video Display</h2>
              <video
                src={videoUrl}
                controls
                className="w-full max-w-3xl rounded shadow"
              />
            </div>
          )}

          <QueryInput
            videoUrl={videoUrl}
            setAnswer={setAnswer}
            setLoading={setLoading}
            setError={setError}
            setAnswerTimestamp={setAnswerTimestamp}
          />

          <AnswerDisplay answer={answer} loading={loading} error={error} />
        </main>

        {/* Right Sidebar */}
        <aside className="w-64 bg-gray-300 p-4 shadow-lg overflow-y-auto flex flex-col items-center">
          <div className="mt-4 w-full flex flex-col items-center">
            <h2 className="text-2xl font-semibold mb-4">Video Preview</h2>

            {videoUrl ? (
              <>
                {/* First 10 seconds preview */}
                <video
                  ref={previewVideoRef}
                  src={videoUrl}
                  muted
                  playsInline
                  className="w-full rounded shadow"
                  onTimeUpdate={(e) => {
                    if (e.currentTarget.currentTime > 10) {
                      e.currentTarget.pause();
                      e.currentTarget.currentTime = 0;
                    }
                  }}
                />
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => {
                      if (previewVideoRef.current) {
                        previewVideoRef.current.currentTime = 0;
                        previewVideoRef.current.play();
                      }
                    }}
                    className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
                  >
                    Play
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2 italic">
                  Preview: first 10 seconds
                </p>

                {/* Timestamp preview */}
                {answerTimestamp !== null && (
                  <>
                    <h3 className="text-lg font-semibold mt-6 mb-2">
                      Answer Timestamp Preview
                    </h3>
                    <video
                      src={videoUrl}
                      ref={answerVideoRef}
                      muted
                      controls
                      className="w-full rounded shadow"
                      onLoadedMetadata={() => {
                        if (answerVideoRef.current) {
                          answerVideoRef.current.currentTime = answerTimestamp;
                          answerVideoRef.current.pause();
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        if (answerVideoRef.current) {
                          answerVideoRef.current.currentTime = answerTimestamp;
                          answerVideoRef.current.play();
                        }
                      }}
                      className="mt-2 px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm font-medium"
                    >
                      Play from {formatTime(answerTimestamp)}
                    </button>
                    <p className="text-xs text-gray-500 mt-1 italic">
                      Preview at {formatTime(answerTimestamp)}
                    </p>
                  </>
                )}
              </>
            ) : (
              <p className="text-gray-500">No video selected.</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

export default App;
