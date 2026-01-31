"use strict";
/**
 * Unified Type Definitions - Single Source of Truth
 * v3.7.6 - All product, navigation, and catalog types
 *
 * ⚠️  REAL DATA ONLY: All types validated against actual roland.json structure
 * Generated: 2026-01-23
 * Status: 0 implicit `any` types - 100% strict typing
 *
 * New in v3.7.6:
 * - Product classification system (MI, PA, Accessories, Cases, Cables)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSecondaryClasses = exports.getProductClass = exports.getClassLabel = exports.getClassIcon = exports.filterByClass = exports.classifyProduct = exports.CATEGORY_CLASSIFICATION_OVERRIDES = exports.BRAND_CLASSIFICATIONS = void 0;
var productClassification_1 = require("./productClassification");
Object.defineProperty(exports, "BRAND_CLASSIFICATIONS", { enumerable: true, get: function () { return productClassification_1.BRAND_CLASSIFICATIONS; } });
Object.defineProperty(exports, "CATEGORY_CLASSIFICATION_OVERRIDES", { enumerable: true, get: function () { return productClassification_1.CATEGORY_CLASSIFICATION_OVERRIDES; } });
Object.defineProperty(exports, "classifyProduct", { enumerable: true, get: function () { return productClassification_1.classifyProduct; } });
Object.defineProperty(exports, "filterByClass", { enumerable: true, get: function () { return productClassification_1.filterByClass; } });
Object.defineProperty(exports, "getClassIcon", { enumerable: true, get: function () { return productClassification_1.getClassIcon; } });
Object.defineProperty(exports, "getClassLabel", { enumerable: true, get: function () { return productClassification_1.getClassLabel; } });
Object.defineProperty(exports, "getProductClass", { enumerable: true, get: function () { return productClassification_1.getProductClass; } });
Object.defineProperty(exports, "getSecondaryClasses", { enumerable: true, get: function () { return productClassification_1.getSecondaryClasses; } });
