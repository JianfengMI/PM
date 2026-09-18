import { fetchBoard, updateBoard } from "@/lib/api";
import { initialData } from "@/lib/kanban";

describe("board API client", () => {
  const credentials = { username: "user", password: "password" };

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads the authenticated board", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(initialData), { status: 200 })
    );

    await expect(fetchBoard(credentials)).resolves.toEqual(initialData);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/board"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Basic dXNlcjpwYXNzd29yZA==",
        }),
      })
    );
  });

  it("updates the authenticated board", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(initialData), { status: 200 })
    );

    await updateBoard(initialData, credentials);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/board"),
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify(initialData),
      })
    );
  });

  it("reports API failures", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response("", { status: 500 })
    );

    await expect(fetchBoard(credentials)).rejects.toThrow("API request failed: 500");
  });
});
