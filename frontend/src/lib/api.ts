/**
 * API client for Swasthya Path backend
 */

import {
  UploadReportResponse,
  TimelineResponse,
  SavingsResponse,
  ReportListResponse,
  DemoSetupResponse,
  HealthResponse,
  DuplicateDecision,
  MedicalReport,
} from "@/types";

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

/**
 * Get access token from localStorage
 */
function getAccessToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("access_token");
  }
  return null;
}

/**
 * Generic fetch wrapper with error handling and auth
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Add authorization header if token exists
  const token = getAccessToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token && !endpoint.includes("/auth/")) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = "An error occurred";
    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText;
    }
    throw new ApiError(errorMessage, response.status);
  }

  return response.json();
}

// ==================== AUTHENTICATION ====================

export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface SignupData {
  email: string;
  password: string;
  name: string;
  phone?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

/**
 * Sign up a new user
 */
export async function signup(data: SignupData): Promise<AuthResponse> {
  const response = await fetchApi<AuthResponse>("/api/auth/signup", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  // Store tokens in localStorage
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", response.access_token);
    localStorage.setItem("refresh_token", response.refresh_token);
    localStorage.setItem("user", JSON.stringify(response.user));
  }

  return response;
}

/**
 * Log in an existing user
 */
export async function login(data: LoginData): Promise<AuthResponse> {
  const response = await fetchApi<AuthResponse>("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  // Store tokens in localStorage
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", response.access_token);
    localStorage.setItem("refresh_token", response.refresh_token);
    localStorage.setItem("user", JSON.stringify(response.user));
  }

  return response;
}

/**
 * Refresh access token
 */
export async function refreshAccessToken(): Promise<AuthResponse> {
  const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;

  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  const response = await fetchApi<AuthResponse>("/api/auth/refresh", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  // Update tokens in localStorage
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", response.access_token);
    localStorage.setItem("user", JSON.stringify(response.user));
  }

  return response;
}

/**
 * Log out user
 */
export async function logout(): Promise<void> {
  const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;

  if (refreshToken) {
    try {
      await fetchApi("/api/auth/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch (error) {
      // Ignore errors during logout
      console.error("Logout error:", error);
    }
  }

  // Clear localStorage
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }
}

/**
 * Get current user info
 */
export async function getCurrentUser(): Promise<User> {
  return fetchApi<User>("/api/auth/me");
}

// ==================== HEALTH CHECK ====================
/**
 * Health check
 */
export async function checkHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>("/health");
}

/**
 * Upload a medical report for analysis
 */
export async function uploadReport(
  file: File,
  userId: string,
  context?: string
): Promise<UploadReportResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", userId);
  if (context) {
    formData.append("context", context);
  }

  return fetchApi<UploadReportResponse>("/api/upload-report", {
    method: "POST",
    body: formData,
  });
}

/**
 * Update duplicate alert decision
 */
export async function updateDuplicateDecision(
  alertId: string,
  decision: DuplicateDecision
): Promise<{ success: boolean; alert_id: string; decision: string; message: string }> {
  return fetchApi(`/api/duplicate-decision/${alertId}?decision=${decision}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
}

/**
 * Get all reports for a user
 */
export async function getReports(userId: string): Promise<ReportListResponse> {
  return fetchApi<ReportListResponse>(`/api/reports/${userId}`);
}

/**
 * Get a specific report
 */
export async function getReport(reportId: string): Promise<MedicalReport> {
  return fetchApi<MedicalReport>(`/api/report/${reportId}`);
}

/**
 * Get user timeline
 */
export async function getTimeline(userId: string): Promise<TimelineResponse> {
  return fetchApi<TimelineResponse>(`/api/timeline/${userId}`);
}

/**
 * Get user savings summary
 */
export async function getSavings(userId: string): Promise<SavingsResponse> {
  return fetchApi<SavingsResponse>(`/api/savings/${userId}`);
}

/**
 * Setup demo data
 */
export async function setupDemo(): Promise<DemoSetupResponse> {
  return fetchApi<DemoSetupResponse>("/api/demo/setup", {
    method: "POST",
  });
}

/**
 * Get demo user info
 */
export async function getDemoUser(): Promise<{
  user_id: string;
  name: string;
  age: number;
  gender: string;
}> {
  return fetchApi("/api/demo/user");
}

/**
 * Combined hook-friendly function to load initial data
 */
export async function loadUserData(userId: string) {
  const [timeline, savings, reports] = await Promise.all([
    getTimeline(userId),
    getSavings(userId),
    getReports(userId),
  ]);

  return {
    timeline,
    savings,
    reports,
  };
}


