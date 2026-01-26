/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";
import { BrandFileSchema } from "../../src/lib/schemas";

describe("Deep Brand File Validation", () => {
  it("should validate boss.json structure", () => {
    // Correct path based on list_dir output
    const filePath = path.join(__dirname, "../../public/data/boss.json");

    if (!fs.existsSync(filePath)) {
      console.error(`File not found at: ${filePath}`);
      throw new Error(`File not found at ${filePath}`);
    }

    const rawData = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = BrandFileSchema.safeParse(rawData);

    if (!result.success) {
      console.error(
        "BOSS Validation Errors:",
        JSON.stringify(result.error.flatten(), null, 2),
      );
    }
    expect(result.success).toBe(true);
  });

  it("should validate nord.json structure", () => {
    // Correct path based on list_dir output
    const filePath = path.join(__dirname, "../../public/data/nord.json");

    if (!fs.existsSync(filePath)) {
      console.error(`File not found at: ${filePath}`);
      throw new Error(`File not found at ${filePath}`);
    }

    const rawData = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const result = BrandFileSchema.safeParse(rawData);

    if (!result.success) {
      console.error(
        "NORD Validation Errors:",
        JSON.stringify(result.error.flatten(), null, 2),
      );
    }
    expect(result.success).toBe(true);
  });
});
