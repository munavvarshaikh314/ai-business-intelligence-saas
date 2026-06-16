/**
 * Central error message translator.
 * Converts raw API errors into human-readable messages.
 */

const ERROR_MAP = {
  // Auth
  "Invalid email or password": "Incorrect email or password. Please try again.",
  "Invalid or expired token": "Your session has expired. Please login again.",
  "Email already registered": "An account with this email already exists. Try logging in.",
  "User not found": "No account found with this email.",
  "Not authenticated": "Please login to continue.",

  // Credits
  "Insufficient credits": "You don't have enough credits. Please buy more to continue.",
  "No credits remaining": "You've run out of credits. Top up to keep going.",

  // Dataset
  "Dataset not found": "This dataset no longer exists. Please create a new one.",
  "Access denied": "You don't have permission to access this dataset.",

  // Upload
  "File too large": "This file is too large. Please upload a file under 50MB.",
  "Invalid file type": "This file type is not supported. Please upload a CSV or PDF.",
  "Failed to parse CSV": "We couldn't read your CSV. Check that it has proper column headers and try again.",
  "Failed to process PDF": "We couldn't process your PDF. Make sure it's not password-protected and try again.",

  // Payment
  "Payment order not found": "Payment record not found. Please try again.",
  "Payment verification failed": "Payment could not be verified. If money was deducted, contact support.",
  "Razorpay keys not configured": "Payments are not set up yet. Please contact support.",

  // Chat
  "Session not found": "Chat session not found. Please start a new chat.",
  "Failed to generate answer": "I couldn't generate an answer. Please try rephrasing your question.",

  // OpenAI / LLM errors
  "insufficient_funds": "AI service quota exhausted. Please contact support or try again later.",
  "You exceeded your current quota": "AI service quota exhausted. Please contact support.",
  "openai": "AI service is temporarily unavailable. Please try again in a moment.",
  "RateLimitError": "Too many requests to AI service. Please wait a moment and try again.",
  "APIConnectionError": "Could not connect to AI service. Please try again shortly.",
  "AuthenticationError": "AI service configuration error. Please contact support.",

  // General
  "Internal server error": "Something went wrong on our end. Please try again in a moment.",
  "Service unavailable": "The service is temporarily unavailable. Please try again shortly.",
};

const HTTP_STATUS_MAP = {
  400: "Invalid request. Please check your input and try again.",
  401: "Your session has expired. Please login again.",
  403: "You don't have permission to do this.",
  404: "The requested resource was not found.",
  409: "A conflict occurred. This item may already exist.",
  413: "The file you uploaded is too large.",
  422: "Some required information is missing or invalid.",
  429: "Too many requests. Please wait a moment and try again.",
  500: "Something went wrong on our end. Please try again.",
  502: "Server is temporarily unavailable. Please try again shortly.",
  503: "Service is under maintenance. Please check back soon.",
};

export function getErrorMessage(err, fallback = "Something went wrong. Please try again.") {
  if (!err) return fallback;

  // Network error — server not reachable
  if (err.code === "ERR_NETWORK" || err.message === "Network Error") {
    // Check if it might be an OpenAI issue from the response
    const detail = err?.response?.data?.detail || "";
    if (
      detail.toLowerCase().includes("openai") ||
      detail.toLowerCase().includes("quota") ||
      detail.toLowerCase().includes("insufficient_funds") ||
      detail.toLowerCase().includes("ratelimit")
    ) {
      return "AI service quota exhausted. Please top up your OpenAI credits or contact support.";
    }
    return "Cannot reach the server. Please check your connection and try again.";
  }

  // Axios timeout
  if (err.code === "ECONNABORTED") {
    return "The request timed out. Please try again.";
  }

  const detail = err?.response?.data?.detail;
  const status = err?.response?.status;

  // Check for OpenAI-specific errors in detail
  if (detail && typeof detail === "string") {
    const lower = detail.toLowerCase();
    if (
      lower.includes("openai") ||
      lower.includes("quota") ||
      lower.includes("insufficient_funds") ||
      lower.includes("you exceeded") ||
      lower.includes("ratelimiterror") ||
      lower.includes("billing")
    ) {
      return "AI service quota exhausted. Please top up your OpenAI credits or contact support.";
    }
  }

  // Try exact match in error map
  if (detail && typeof detail === "string") {
    const mapped = ERROR_MAP[detail];
    if (mapped) return mapped;

    // Try partial match
    for (const [key, message] of Object.entries(ERROR_MAP)) {
      if (detail.toLowerCase().includes(key.toLowerCase())) {
        return message;
      }
    }

    // If detail is technical, hide it
    const isTechnical = /traceback|exception|sqlalchemy|psycopg|fastapi|uvicorn|line \d+/i.test(detail);
    if (!isTechnical && detail.length < 150) {
      return detail;
    }
  }

  // Fall back to HTTP status message
  if (status && HTTP_STATUS_MAP[status]) {
    return HTTP_STATUS_MAP[status];
  }

  return fallback;
}

export const AuthErrors = {
  login: (err) => getErrorMessage(err, "Login failed. Please check your credentials."),
  register: (err) => getErrorMessage(err, "Registration failed. Please try again."),
  session: (err) => getErrorMessage(err, "Session error. Please login again."),
};

export const UploadErrors = {
  csv: (err) => getErrorMessage(err, "CSV upload failed. Please check your file and try again."),
  pdf: (err) => getErrorMessage(err, "PDF upload failed. Please check your file and try again."),
};

export const ChatErrors = {
  send: (err) => getErrorMessage(err, "Failed to send message. Please try again."),
  session: (err) => getErrorMessage(err, "Failed to load chat. Please refresh the page."),
  history: (err) => getErrorMessage(err, "Failed to load chat history."),
};

export const DatasetErrors = {
  create: (err) => getErrorMessage(err, "Failed to create dataset. Please try again."),
  load: (err) => getErrorMessage(err, "Failed to load datasets. Please refresh the page."),
  delete: (err) => getErrorMessage(err, "Failed to delete dataset. Please try again."),
};

export const PaymentErrors = {
  order: (err) => getErrorMessage(err, "Failed to create payment order. Please try again."),
  verify: (err) => getErrorMessage(err, "Payment verification failed. If money was deducted, contact support."),
};
