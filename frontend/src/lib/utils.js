export function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

export function formatNumber(num) {
  if (num === null || num === undefined) return "—";
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
  if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
  return Number(num).toLocaleString();
}

export function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric"
  });
}

export function truncate(str, length = 80) {
  if (!str) return "";
  return str.length > length ? str.slice(0, length) + "…" : str;
}

export function sleep(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

export function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
