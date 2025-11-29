import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format currency in Indian Rupees
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

/**
 * Format date with time
 */
export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

/**
 * Calculate days ago from a date string
 */
export function daysAgo(dateString: string): number {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * Get relative time string
 */
export function getRelativeTime(dateString: string): string {
  const days = daysAgo(dateString);
  
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;
  if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
  if (days < 365) return `${Math.floor(days / 30)} months ago`;
  return `${Math.floor(days / 365)} years ago`;
}

/**
 * Get status color class
 */
export function getStatusColor(status: string): string {
  switch (status?.toLowerCase()) {
    case "normal":
      return "status-normal";
    case "abnormal":
      return "status-abnormal";
    case "critical":
      return "status-critical";
    default:
      return "bg-gray-100 text-gray-800";
  }
}

/**
 * Get status badge variant
 */
export function getStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  switch (status?.toLowerCase()) {
    case "normal":
      return "default";
    case "abnormal":
      return "secondary";
    case "critical":
      return "destructive";
    default:
      return "outline";
  }
}

/**
 * Get category icon name (for Lucide icons)
 */
export function getCategoryIcon(category: string): string {
  switch (category?.toLowerCase()) {
    case "blood":
      return "Droplet";
    case "imaging":
      return "Scan";
    case "vitals":
      return "Heart";
    case "urine":
      return "FlaskConical";
    default:
      return "FileText";
  }
}

/**
 * Validate file type
 */
export function isValidFileType(file: File): boolean {
  const validTypes = ["image/jpeg", "image/png", "image/jpg", "application/pdf"];
  return validTypes.includes(file.type);
}

/**
 * Validate file size (max 10MB)
 */
export function isValidFileSize(file: File, maxSizeMB: number = 10): boolean {
  return file.size <= maxSizeMB * 1024 * 1024;
}

/**
 * Convert file to base64
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      // Remove data URL prefix
      const base64 = result.split(",")[1];
      resolve(base64);
    };
    reader.onerror = (error) => reject(error);
  });
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

/**
 * Generate a random demo user ID
 */
export function generateDemoUserId(): string {
  return `demo-user-${Date.now()}`;
}

/**
 * Get stored user ID or create demo
 */
export function getUserId(): string {
  if (typeof window === "undefined") return "demo-user-123";
  
  let userId = localStorage.getItem("swasthya_user_id");
  if (!userId) {
    userId = "demo-user-123"; // Default demo user
    localStorage.setItem("swasthya_user_id", userId);
  }
  return userId;
}

/**
 * Set user ID in storage
 */
export function setUserId(userId: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("swasthya_user_id", userId);
  }
}


