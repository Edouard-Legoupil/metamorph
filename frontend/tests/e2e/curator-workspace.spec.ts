import { test, expect } from '@playwright/test';

test('End-to-end curation: create draft, prefill, validate, submit, approve', async ({ page }) => {
  // Login step (adapt for SSO/hardcoded test user)
  await page.goto('/curation');
  await page.click('text=Create New Card');
  await page.click('text=KC-2'); // select Field Context Card
  await expect(page.locator('text=Draft generated from graph')).toBeVisible();
  await page.click('text=Population Profile');
  // Prefilled with graph data?
  await expect(page.locator('textarea')).toContainText('Refugee');
  // Try typing/editing
  await page.fill('textarea', 'Test narrative for population profile');
  // Check word count enforcement
  await expect(page.locator('.word-count-bar')).toHaveAttribute('aria-valuenow');
  // Try saving
  await page.click('text=Save');
  // Submit for review
  await page.click('text=Submit for Review');
  // Should now appear in curation queue/dashboard
  await page.goto('/curation');
  await page.click('text=UNDER_REVIEW');
  await expect(page.locator('text=Test narrative for population profile')).toBeVisible();
  // Approve
  await page.click('text=Approve');
  await expect(page.locator('text=APPROVED')).toBeVisible();
});
