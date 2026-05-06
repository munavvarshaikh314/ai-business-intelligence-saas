import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <header className="flex justify-between items-center px-8 py-5 border-b">
        <h1 className="text-xl font-bold">AI BI RAG Dashboard</h1>

        <div className="flex gap-4">
          <Link
            href="/login"
            className="px-4 py-2 rounded border hover:bg-gray-100"
          >
            Login
          </Link>

          <Link
            href="/register"
            className="px-4 py-2 rounded bg-black text-white hover:bg-gray-800"
          >
            Register
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="px-8 py-20 text-center">
        <h2 className="text-4xl font-bold max-w-3xl mx-auto leading-tight">
          AI-Powered Business Intelligence Dashboard with RAG + SQL + ML Agents
        </h2>

        <p className="text-gray-600 mt-5 max-w-2xl mx-auto text-lg">
          Upload CSV/PDF data, get instant analytics dashboards, and ask questions
          in natural language using RAG + Text-to-SQL + ML predictions.
        </p>

        <div className="flex justify-center gap-4 mt-8">
          <Link
            href="/register"
            className="px-6 py-3 rounded bg-black text-white hover:bg-gray-800"
          >
            Get Started Free
          </Link>

          <Link
            href="/login"
            className="px-6 py-3 rounded border hover:bg-gray-100"
          >
            Login
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="px-8 py-16 bg-gray-50">
        <h3 className="text-3xl font-bold text-center mb-12">
          Why This Platform?
        </h3>

        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <div className="bg-white p-6 rounded shadow">
            <h4 className="font-bold text-lg mb-2">📊 Analytics Dashboard</h4>
            <p className="text-gray-600 text-sm">
              Auto-generate KPIs, trends, category breakdown, and region insights
              from uploaded CSV data.
            </p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <h4 className="font-bold text-lg mb-2">🤖 RAG Chatbot</h4>
            <p className="text-gray-600 text-sm">
              Ask questions directly from PDFs with citations, chunking, hybrid search,
              reranking, and confidence scoring.
            </p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <h4 className="font-bold text-lg mb-2">🧠 SQL + ML Agent</h4>
            <p className="text-gray-600 text-sm">
              Convert natural language to SQL safely and run predictions like churn/sales forecasting.
            </p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <h4 className="font-bold text-lg mb-2">💳 Credits + Payments</h4>
            <p className="text-gray-600 text-sm">
              Razorpay integration with credit-based usage tracking, invoices, and payment history.
            </p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <h4 className="font-bold text-lg mb-2">🔐 Secure SaaS</h4>
            <p className="text-gray-600 text-sm">
              JWT auth, dataset isolation, SQL guard, prompt injection protection,
              and rate limiting.
            </p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <h4 className="font-bold text-lg mb-2">📡 Streaming AI Responses</h4>
            <p className="text-gray-600 text-sm">
              Real-time WebSocket token streaming for ChatGPT-like smooth responses.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="px-8 py-16">
        <h3 className="text-3xl font-bold text-center mb-12">
          Simple Pricing
        </h3>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <div className="border p-6 rounded shadow-sm">
            <h4 className="text-xl font-bold">Starter</h4>
            <p className="text-gray-600 mt-2">For students & testing</p>
            <p className="text-3xl font-bold mt-4">₹0</p>
            <p className="text-sm text-gray-600 mt-2">50 Free Credits</p>
          </div>

          <div className="border p-6 rounded shadow-sm bg-gray-50">
            <h4 className="text-xl font-bold">Pro</h4>
            <p className="text-gray-600 mt-2">For professionals</p>
            <p className="text-3xl font-bold mt-4">₹199</p>
            <p className="text-sm text-gray-600 mt-2">200 Credits</p>
          </div>

          <div className="border p-6 rounded shadow-sm">
            <h4 className="text-xl font-bold">Enterprise</h4>
            <p className="text-gray-600 mt-2">For teams</p>
            <p className="text-3xl font-bold mt-4">Custom</p>
            <p className="text-sm text-gray-600 mt-2">
              Unlimited datasets + admin controls
            </p>
          </div>
        </div>

        <div className="text-center mt-10">
          <Link
            href="/register"
            className="px-6 py-3 rounded bg-black text-white hover:bg-gray-800"
          >
            Start Now
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-8 py-8 border-t text-center text-sm text-gray-500">
        © {new Date().getFullYear()} AI BI RAG Dashboard. Built with FastAPI + Next.js.
      </footer>
    </div>
  );
}