"use client";

export default function MLResultViewer({ result }) {
  if (!result) return null;

  return (
    <div className="mt-3 border rounded bg-white p-4 shadow">
      <h3 className="font-semibold text-sm mb-2">ML Prediction</h3>

      <p className="text-sm">
        <span className="font-semibold">Target:</span> {result.target_column}
      </p>

      <p className="text-sm">
        <span className="font-semibold">Prediction:</span> {result.prediction}
      </p>

      {result.confidence !== null && result.confidence !== undefined && (
        <p className="text-sm">
          <span className="font-semibold">Confidence:</span>{" "}
          {(result.confidence * 100).toFixed(2)}%
        </p>
      )}

      <p className="text-xs text-gray-500 mt-2">
        Model: {result.model_name}
      </p>
    </div>
  );
}