import { test } from '@playwright/test';
test('diagnostic', async ({ page }) => {
  const failed500: string[] = [];
  const pageErrors: string[] = [];
  page.on('response', r => { if (r.status() >= 500) failed500.push(r.status()+' '+r.url()); });
  page.on('pageerror', e => pageErrors.push('PAGEERROR: '+e.message));
  await page.goto('/');
  await page.waitForTimeout(6000);
  const headings = await page.evaluate(() =>
    Array.from(document.querySelectorAll('h1,h2,h3')).map(h => h.tagName+':'+h.textContent?.trim())
  );
  console.log('HEADINGS:'+JSON.stringify(headings));
  console.log('500s:'+JSON.stringify(failed500));
  console.log('ERRORS:'+JSON.stringify(pageErrors));
});
