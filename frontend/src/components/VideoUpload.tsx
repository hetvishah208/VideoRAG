import React, { useState } from 'react';

interface Props {
  setVideoUrl: (url: string) => void;
  setError: (error: string | null) => void;
}

const MAX_FILE_SIZE_MB = 100;

const VideoUpload: React.FC<Props> = ({ setVideoUrl, setError }) => {
  const [loading, setLoading] = useState(false);
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setLoading(true);

    if (!file.type.startsWith('video/')) {
      setError('Please upload a valid video file.');
      setLoading(false);
      return;
    }

    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > MAX_FILE_SIZE_MB) {
      setError(`File size exceeds ${MAX_FILE_SIZE_MB}MB.`);
      setLoading(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Upload failed");
      }
    //process the response of the server
      const data = await res.json();
      const fullUrl = `http://localhost:8000${data.url}`;
      setVideoUrl(fullUrl);
      setUploadedFilename(data.filename);
      
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative h-full">
      <label htmlFor="video-upload" className="block text-2xl font-semibold mt-30 mb-4">
        Upload a Video
      </label>
      <input
        id="video-upload"
        type="file"
        accept="video/*"
        onChange={handleFileChange}
        className="block mb-2 bg-white rounded border p-2 cursor-pointer w-full"
        disabled={loading}
      />
      {loading && <p className="text-blue-500 mt-1">Uploading video...</p>}

      {uploadedFilename && (
        <div className="mt-4 text-sm text-gray-700">
          <strong>Uploaded:</strong> {uploadedFilename}
        </div>
      )}
    </div>
  );
};

export default VideoUpload;
