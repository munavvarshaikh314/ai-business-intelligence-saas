import axios from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
  timeout: 30000,
});

// Request interceptor — attach token
api.interceptors.request.use((config) => {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — only redirect on 401 if user was previously logged in
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const url = error?.config?.url || "";

    // Never redirect on auth routes — let the component handle those
    const isAuthRoute =
      url.includes("/auth/login") ||
      url.includes("/auth/register") ||
      url.includes("/auth/me");

    if (status === 401 && !isAuthRoute && typeof window !== "undefined") {
      const token = localStorage.getItem("token");

      // Only redirect if there WAS a token — means it expired
      // If no token existed, this is just an unauthenticated page load
      if (token) {
        localStorage.removeItem("token");
        if (!window.location.pathname.includes("/login")) {
          window.location.href = "/login?reason=session_expired";
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;




// import axios from "axios";

// const API_BASE_URL =
//   process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// const api = axios.create({
//   baseURL: API_BASE_URL,
//   withCredentials: false,
// });

// api.interceptors.request.use((config) => {
//   const token =
//     typeof window !== "undefined" ? localStorage.getItem("token") : null;

//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }

//   return config;
// });

// export default api;