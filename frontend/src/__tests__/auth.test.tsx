import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { login, signup, logout, getCurrentUser } from "@/lib/api";
import { useRouter } from "next/navigation";

// Mock API functions
jest.mock("@/lib/api");
jest.mock("next/navigation", () => ({
    useRouter: jest.fn(),
}));

const mockUser = {
    id: "test-user-123",
    email: "test@example.com",
    name: "Test User",
};

// Test component to consume AuthContext
const TestComponent = () => {
    const { user, login, logout, isAuthenticated, isLoading } = useAuth();

    if (isLoading) return <div>Loading...</div>;

    return (
        <div>
            {isAuthenticated ? (
                <>
                    <div data-testid="user-email">{user?.email}</div>
                    <button onClick={logout}>Logout</button>
                </>
            ) : (
                <button onClick={() => login({ email: "test@example.com", password: "password" })}>
                    Login
                </button>
            )}
        </div>
    );
};

describe("AuthContext", () => {
    const mockPush = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
        (getCurrentUser as jest.Mock).mockResolvedValue(null); // Default to logged out
    });

    it("mock works", async () => {
        (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
        const user = await getCurrentUser();
        expect(user).toEqual(mockUser);
    });

    it("provides authentication state", async () => {
        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        // Initial state might be loading, but we wait for Login button
        await waitFor(() => {
            expect(screen.getByText("Login")).toBeInTheDocument();
        });
    });

    it("handles login success", async () => {
        (login as jest.Mock).mockResolvedValue({
            access_token: "token",
            user: mockUser,
        });
        (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => expect(screen.queryByText("Loading...")).not.toBeInTheDocument());

        fireEvent.click(screen.getByText("Login"));

        await waitFor(() => {
            expect(login).toHaveBeenCalledWith({ email: "test@example.com", password: "password" });
            expect(screen.getByTestId("user-email")).toHaveTextContent("test@example.com");
        });
    });

    it("handles logout", async () => {
        // Start as logged in
        (getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByText("Logout")).toBeInTheDocument();
            expect(getCurrentUser).toHaveBeenCalled();
        });

        fireEvent.click(screen.getByText("Logout"));

        await waitFor(() => {
            expect(logout).toHaveBeenCalled();
            expect(screen.getByText("Login")).toBeInTheDocument();
            expect(mockPush).toHaveBeenCalledWith("/auth");
        });
    });
});
