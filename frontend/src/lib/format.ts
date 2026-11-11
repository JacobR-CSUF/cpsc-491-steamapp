const LOCALE = "en-US";

export function formatCents(cents: number, currency: string): string {
  return new Intl.NumberFormat(LOCALE, {
    style: "currency",
    currency,
  }).format(cents / 100);
}

export function formatHours(minutes: number): string {
  return `${new Intl.NumberFormat(LOCALE, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(minutes / 60)} h`;
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat(LOCALE, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(iso));
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatNumber(value: number, maximumFractionDigits = 0): string {
  return new Intl.NumberFormat(LOCALE, { maximumFractionDigits }).format(value);
}
