"use client";

export default function UploadProgress({ progress }) {
  return (
    <div className="w-full mt-3">
      <div className="w-full bg-gray-200 rounded h-3">
        <div
          className="bg-black h-3 rounded"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-sm text-gray-600 mt-1">{progress}% uploaded</p>
    </div>
  );
}