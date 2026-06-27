import React from 'react';

interface Props {
  answer: string;
  loading: boolean;
  error: string | null;
}

const AnswerDisplay: React.FC<Props> = ({ answer, loading, error }) => {
  return (
    <div className="mt-6 w-full max-w-3xl mx-auto" id="answer-box">
      {loading && (
        <div className="p-4 border rounded bg-blue-50 text-blue-700 font-medium">
          Loading answer...
        </div>
      )}

      {error && (
        <div className="p-4 border rounded bg-red-100 text-red-700 font-medium">
          {error}
        </div>
      )}

      {answer && !loading && !error && (
        <div
          className="p-6 bg-white border border-blue-500 rounded-lg shadow-md min-h-[150px] text-gray-800 leading-relaxed text-lg whitespace-pre-wrap break-words"
        >
          <h3 className="text-xl font-bold text-blue-800 mb-2">Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default AnswerDisplay;
