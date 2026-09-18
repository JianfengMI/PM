import { expect, test } from "@playwright/test";

const signIn = async (page: Parameters<Parameters<typeof test>[1]>[0]["page"]) => {
  await page.goto("/");
  await page.evaluate(() => window.localStorage.clear());
  await page.reload();
  if (await page.getByRole("button", { name: "Create an account instead" }).isVisible()) {
    await page.getByRole("button", { name: "Create an account instead" }).click();
  }
  await page.getByLabel("Username").fill("user");
  await page.getByRole("textbox", { name: "Password", exact: true }).fill("password");
  await page.getByLabel("Confirm password").fill("password");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
};

test("requires sign up, sign in, and supports logout", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => window.localStorage.clear());
  await page.reload();
  await expect(page.getByLabel("Username")).toBeVisible();
  if (await page.getByRole("button", { name: "Create an account instead" }).isVisible()) {
    await page.getByRole("button", { name: "Create an account instead" }).click();
  }
  await expect(page.getByRole("button", { name: "Create account" })).toBeVisible();

  await page.getByLabel("Username").fill("user");
  await page.getByRole("textbox", { name: "Password", exact: true }).fill("wrong");
  await page.getByLabel("Confirm password").fill("different");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByText(/passwords do not match/i)).toBeVisible();

  await page.getByRole("textbox", { name: "Password", exact: true }).fill("password");
  await page.getByLabel("Confirm password").fill("password");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();

  await page.getByLabel("Username").fill("user");
  await page.getByRole("textbox", { name: "Password", exact: true }).fill("password");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page.getByLabel("Username")).toBeVisible();
});

test("shows sign in on a fresh launch", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    window.localStorage.setItem(
      "kanban-studio-account",
      JSON.stringify({ username: "user", password: "password" })
    );
  });
  await page.reload();

  await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
});

test("loads the kanban board", async ({ page }) => {
  await signIn(page);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await signIn(page);
  const cardTitle = `Playwright card ${Date.now()}`;
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill(cardTitle);
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText(cardTitle, { exact: true })).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await signIn(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

test("persists board changes after logout and sign in", async ({ page }) => {
  await signIn(page);
  const persistentCardTitle = `Persistent card ${Date.now()}`;
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill(persistentCardTitle);
  await firstColumn.getByPlaceholder("Details").fill("Saved locally.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText(persistentCardTitle, { exact: true })).toBeVisible();

  await page.getByRole("button", { name: "Log out" }).click();
  await page.getByRole("textbox", { name: "Username" }).fill("user");
  await page.getByRole("textbox", { name: "Password", exact: true }).fill("password");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page.getByText(persistentCardTitle, { exact: true })).toBeVisible();
});

test("chat assistant responds and refreshes the board", async ({ page }) => {
  await signIn(page);
  const boardResponse = await page.request.get("http://127.0.0.1:8000/api/board", {
    headers: { Authorization: "Basic dXNlcjpwYXNzd29yZA==" },
  });
  const board = await boardResponse.json();
  const assistantCard = {
    id: `ai-card-${Date.now()}`,
    title: "Assistant follow-up",
    details: "Created from chat.",
  };
  board.cards[assistantCard.id] = assistantCard;
  board.columns[0].cardIds.push(assistantCard.id);

  await page.route("**/api/ai/chat", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        response: "I added the follow-up card.",
        board,
        board_updated: true,
      }),
    });
  });

  await page.getByLabel("Your question").fill("Add a follow-up card.");
  await page.getByLabel("Your question").press("Enter");

  await expect(page.getByText("Add a follow-up card.", { exact: true })).toBeVisible();
  await expect(page.getByText("I added the follow-up card.")).toBeVisible();
  await expect(page.getByText("Assistant follow-up", { exact: true })).toBeVisible();
});
