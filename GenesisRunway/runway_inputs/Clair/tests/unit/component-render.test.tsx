import { render, screen, waitFor } from "@testing-library/react";
import ClairAppShell from "@/components/ClairAppShell";

const push = jest.fn();
const replace = jest.fn();
const router = { push, replace };

jest.mock("next/navigation", () => ({
  useRouter: () => router,
}));

beforeEach(() => {
  push.mockReset();
  replace.mockReset();
  global.fetch = jest.fn(() => new Promise(() => undefined)) as jest.Mock;
});

function mockAuthenticatedSession() {
  global.fetch = jest.fn((url) => {
    if (String(url).endsWith("/api/session")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          user: { id: "user-patient", email: "patient@example.com", name: "Maya Rao", role: "patient" },
          session: { id: "session-user-patient", userId: "user-patient", expiresAt: "", uploadedDocumentIds: [] },
        }),
      });
    }
    return new Promise(() => undefined);
  }) as jest.Mock;
}

test("renders the home experience", async () => {
  render(<ClairAppShell view="home" />);

  expect(screen.getByRole("heading", { name: /Clinical AI Navigation Platform/i })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: /Login to CLAIR/i })).toBeInTheDocument();
  expect(screen.getByLabelText("Email")).toHaveValue("patient@example.com");
  await waitFor(() => expect(global.fetch).toHaveBeenCalledWith("/api/session"));
});

test("renders the login form with demo fields", () => {
  render(<ClairAppShell view="login" />);

  expect(screen.getByRole("heading", { name: /Clinical AI Navigation Platform/i })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: /Login to CLAIR/i })).toBeInTheDocument();
  expect(screen.getByLabelText("Email")).toHaveValue("patient@example.com");
  expect(screen.getByLabelText("Access code")).toHaveValue("patient123");
});

test("renders document upload with a disabled summarize action until a PDF is selected", async () => {
  mockAuthenticatedSession();
  render(<ClairAppShell view="documents" />);

  expect(await screen.findByRole("heading", { name: /document intelligence/i })).toBeInTheDocument();
  expect(screen.getByLabelText("PDF file")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /analyze real report/i })).toBeDisabled();
});

test("shows a profile pill instead of login when a session exists", async () => {
  mockAuthenticatedSession();

  render(<ClairAppShell view="dashboard" />);

  expect(await screen.findByRole("button", { name: /logout/i })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "Login" })).not.toBeInTheDocument();
});
