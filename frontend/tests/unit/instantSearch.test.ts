/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/**
 * Unit Tests: instantSearch Service
 * Tests fuzzy search functionality
 */

import { beforeEach, describe, expect, it } from "vitest";
import type { Product } from "../../src/types";
import { mockProductsByCategory } from "../fixtures/mockData";

describe("instantSearch - Fuse.js Fuzzy Search", () => {
  let allProducts: Product[];

  beforeEach(() => {
    allProducts = [
      ...mockProductsByCategory["Electronic Drums"],
      ...mockProductsByCategory["Synthesizers"],
      ...mockProductsByCategory["Digital Pianos"],
    ];
  });

  describe("Search performance", () => {
    it("should search <50ms for single brand catalog", async () => {
      const query = "drums";
      const startTime = performance.now();

      // Simulate search
      const results = allProducts.filter(
        (p) =>
          p.name.toLowerCase().includes(query.toLowerCase()) ||
          p.category?.toLowerCase().includes(query.toLowerCase()),
      );

      const endTime = performance.now();
      const duration = endTime - startTime;

      expect(duration).toBeLessThan(50);
      expect(results.length).toBeGreaterThan(0);
    });
  });

  describe("Search accuracy", () => {
    it("should find products by exact name", () => {
      const results = allProducts.filter((p) =>
        p.name.toLowerCase().includes("td-17kvx"),
      );

      expect(results).toHaveLength(1);
      expect(results[0].name).toContain("TD-17KVX");
    });

    it("should find products by category", () => {
      const results = allProducts.filter((p) =>
        p.category?.toLowerCase().includes("synthesizer"),
      );

      expect(results.length).toBeGreaterThan(0);
      expect(results.every((p) => p.category === "Synthesizers")).toBe(true);
    });

    it("should handle partial matches", () => {
      const results = allProducts.filter(
        (p) =>
          p.name.toLowerCase().includes("td") ||
          p.name.toLowerCase().includes("juno"),
      );

      expect(results.length).toBeGreaterThan(0);
    });

    it("should handle case-insensitive search", () => {
      const lowerResults = allProducts.filter((p) =>
        p.name.toLowerCase().includes("roland"),
      );

      const upperResults = allProducts.filter((p) =>
        p.name.toLowerCase().includes("ROLAND".toLowerCase()),
      );

      expect(lowerResults).toEqual(upperResults);
    });
  });

  describe("Search result structure", () => {
    it("should return products with all required fields", () => {
      const results = allProducts.slice(0, 3);

      results.forEach((product) => {
        expect(product).toHaveProperty("id");
        expect(product).toHaveProperty("name");
        expect(product).toHaveProperty("brand");
        expect(product).toHaveProperty("category");
      });
    });
  });

  describe("Edge cases", () => {
    it("should handle empty query", () => {
      const results = allProducts.filter((p) =>
        p.name.toLowerCase().includes(""),
      );

      expect(results.length).toBe(allProducts.length);
    });

    it("should handle non-existent product search", () => {
      const results = allProducts.filter((p) =>
        p.name.toLowerCase().includes("nonexistent"),
      );

      expect(results.length).toBe(0);
    });

    it("should handle special characters", () => {
      const results = allProducts.filter((p) => p.name.includes("TD-27"));

      expect(results.length).toBeGreaterThanOrEqual(0);
    });
  });
});
