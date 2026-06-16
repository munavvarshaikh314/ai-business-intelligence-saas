"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { AuthErrors } from "@/lib/errors";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) { setError("Please enter your full name."); return; }
    if (!email.trim()) { setError("Please enter your email."); return; }
    if (password.length < 6) { setError("Password must be at least 6 characters."); return; }

    setLoading(true);
    try {
      await register(name, email, password);
      router.push("/login?registered=true");
    } catch (err) {
      setError(AuthErrors.register(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <form
        onSubmit={handleRegister}
        className="bg-white p-6 rounded-lg shadow-md w-full max-w-md"
      >
        <h1 className="text-2xl font-bold mb-1">Create account</h1>
        <p className="text-sm text-gray-500 mb-5">Get started with NeuralStack AI</p>

        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <input
          className="w-full p-2 border rounded mb-3 outline-none focus:border-emerald-400"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <input
          className="w-full p-2 border rounded mb-3 outline-none focus:border-emerald-400"
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="w-full p-2 border rounded mb-4 outline-none focus:border-emerald-400"
          placeholder="Password (min 6 characters)"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          disabled={loading}
          className="w-full bg-black text-white py-2 rounded font-semibold hover:bg-gray-800 transition disabled:bg-gray-300"
        >
          {loading ? "Creating account..." : "Create Account"}
        </button>

        <p className="text-sm mt-3 text-center">
          Already have an account?{" "}
          <a className="text-emerald-600 underline" href="/login">Login</a>
        </p>
      </form>
    </div>
  );
}


// "use client";

// import { useState } from "react";
// import { useRouter } from "next/navigation";
// import { useAuth } from "@/context/AuthContext";

// export default function RegisterPage() {
//   const { register } = useAuth();
//   const router = useRouter();

//   const [name, setName] = useState("");
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   const [error, setError] = useState("");
//   const [loading, setLoading] = useState(false);

//   const handleRegister = async (e) => {
//     e.preventDefault();
//     setError("");
//     setLoading(true);

//     try {
//       await register(name, email, password);
//       router.push("/login");
//     } catch (err) {
//       setError(err?.response?.data?.detail || "Registration failed");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
//       <form
//         onSubmit={handleRegister}
//         className="bg-white p-6 rounded-lg shadow-md w-full max-w-md"
//       >
//         <h1 className="text-2xl font-bold mb-4">Register</h1>

//         {error && <p className="text-red-500 mb-3">{error}</p>}

//         <input
//           className="w-full p-2 border rounded mb-3"
//           placeholder="Full Name"
//           value={name}
//           onChange={(e) => setName(e.target.value)}
//         />

//         <input
//           className="w-full p-2 border rounded mb-3"
//           placeholder="Email"
//           type="email"
//           value={email}
//           onChange={(e) => setEmail(e.target.value)}
//         />

//         <input
//           className="w-full p-2 border rounded mb-3"
//           placeholder="Password"
//           type="password"
//           value={password}
//           onChange={(e) => setPassword(e.target.value)}
//         />

//         <button
//           disabled={loading}
//           className="w-full bg-black text-white py-2 rounded"
//         >
//           {loading ? "Creating..." : "Register"}
//         </button>

//         <p className="text-sm mt-3">
//           Already have an account?{" "}
//           <a className="text-blue-600 underline" href="/login">
//             Login
//           </a>
//         </p>
//       </form>
//     </div>
//   );
// }