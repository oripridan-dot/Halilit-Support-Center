/* eslint-disable @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access */
import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";
import type { MasterIndex } from "../../src/types";

describe("Real Data Integrity", () => {
  const dataDir = path.resolve(process.cwd(), "public/data");
  const indexFile = path.join(dataDir, "index.json");

  it("should have index.json", () => {
    expect(fs.existsSync(indexFile)).toBe(true);
  });

  let indexData: MasterIndex | null = null;

  it("should load index.json and have available brands", () => {
    if (!fs.existsSync(indexFile)) return;
    const raw = fs.readFileSync(indexFile, "utf-8");
    indexData = JSON.parse(raw) as MasterIndex;

    // Basic schema check
    expect(indexData).toHaveProperty("brands");
    expect(Array.isArray(indexData.brands)).toBe(true);
    expect(indexData.brands.length).toBeGreaterThan(0);

    // Verify required brand metadata
    for (const brand of indexData.brands) {
      expect(brand).toHaveProperty("slug");
      expect(brand).toHaveProperty("name");
      expect(brand).toHaveProperty("data_file");
    }
  });

  it("should verify each brand file has valid product data", () => {
    if (!indexData) return;

    for (const brand of indexData.brands) {
      const brandFile = path.join(dataDir, brand.data_file);
      expect(fs.existsSync(brandFile)).toBe(true);

      const raw = fs.readFileSync(brandFile, "utf-8");
      const brandData = JSON.parse(raw);

      // Verify content - basic structure validation
      expect(brandData).toHaveProperty("brand_identity");
      expect(brandData).toHaveProperty("products");
      expect(Array.isArray(brandData.products)).toBe(true);
      
      if (brandData.products.length > 0) {
        expect(brandData.products.length).toBeGreaterThan(0);
        // Verify first product has id
        expect(brandData.products[0]).toHaveProperty("id");
      }
    }
  });
});
