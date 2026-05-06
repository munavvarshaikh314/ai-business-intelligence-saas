export default function AboutPage() {
  return (
    <div className="p-10 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">About This Project</h1>

      <p className="text-gray-700 leading-relaxed">
        AI BI RAG Dashboard is a full-stack SaaS platform that combines
        Data Science + Generative AI. Users can upload structured datasets (CSV)
        and unstructured documents (PDF), generate dashboards, ask questions
        through RAG chatbot, run SQL analytics, and perform ML predictions.
      </p>
    </div>
  );
}