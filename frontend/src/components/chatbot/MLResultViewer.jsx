"use client";

export default function MLResultViewer({ result }) {
  if (!result || result.query_type !== "PREDICTION") return null;

  const prediction = result.prediction;
  const targetCol =
    result.target_column?.replace(/_/g, " ") || "Value";

  const answer = result.answer || "";
  const inputData = result.input_data || {};

  const category = inputData.Product_Category;
  const region = inputData.Region;
  const quantity = inputData.Quantity_Sold;
  const unitPrice = inputData.Unit_Price;

  const isMonetary =
    /sales|revenue|profit|income|price|amount|cost/i.test(targetCol);

  const formattedPrediction = isMonetary
    ? `₹${Number(prediction).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`
    : typeof prediction === "number"
    ? Number(prediction).toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })
    : prediction;

  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">

      {/* Prediction Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 px-5 py-5">
        <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-emerald-100">
          Predicted {targetCol}
        </p>

        <p className="text-5xl font-bold tracking-tight text-white">
          {formattedPrediction}
        </p>
      </div>

      {/* Input Summary */}
      {(category || region || quantity || unitPrice) && (
        <div className="border-t border-slate-100 px-5 py-4">

          {(category || region) && (
            <p className="text-sm font-medium text-slate-700">
              {[category, region].filter(Boolean).join(" • ")}
            </p>
          )}

          {(quantity || unitPrice) && (
            <p className="mt-1 text-xs text-slate-500">
              {quantity && `Qty: ${quantity}`}
              {quantity && unitPrice && " • "}
              {unitPrice && `Price: ₹${Number(unitPrice).toLocaleString("en-IN")}`}
            </p>
          )}

        </div>
      )}

      {/* Business Insight */}
      <div className="border-t border-slate-100 px-5 py-4">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Business Insight
        </p>

        <p className="text-sm leading-relaxed text-slate-700">
          {answer}
        </p>
      </div>
    </div>
  );
}



// "use client";

// export default function MLResultViewer({ result }) {
//   if (!result) return null;

//   return (
//     <div className="mt-3 border rounded bg-white p-4 shadow">
//       <h3 className="font-semibold text-sm mb-2">ML Prediction</h3>

//       <p className="text-sm">
//         <span className="font-semibold">Target:</span> {result.target_column}
//       </p>

//       <p className="text-sm">
//         <span className="font-semibold">Prediction:</span> {result.prediction}
//       </p>

//       {result.confidence !== null && result.confidence !== undefined && (
//         <p className="text-sm">
//           <span className="font-semibold">Confidence:</span>{" "}
//           {(result.confidence * 100).toFixed(2)}%
//         </p>
//       )}

//       <p className="text-xs text-gray-500 mt-2">
//         Model: {result.model_name}
//       </p>
//     </div>
//   );
// }