/**
 * explorationUtils.ts — Pure helper utilities for ExplorationPanel.
 * Extracted to keep all panel files under the 700-line ceiling.
 */

/** Keys to exclude when unwrapping exploration results. */
export const META_KEYS = new Set([
  "product_id", "action_type", "topic", "format",
  "product", "guideType", "guide_type",
]);

/** Maps section keywords to corresponding icons. */
export const SECTION_ICONS: Record<string, string> = {
  unboxing: "\ud83d\udce6", box: "\ud83d\udce6", whats_in: "\ud83d\udce6", "what's": "\ud83d\udce6",
  setup: "\u2699\ufe0f", physical: "\ud83d\udccf", placement: "\ud83d\udccf", position: "\ud83d\udccf",
  connection: "\ud83d\udd0c", cable: "\ud83d\udd0c", signal: "\ud83d\udd0c", connect: "\ud83d\udd0c",
  power: "\u26a1", calibrat: "\ud83c\udf9a\ufe0f", setting: "\ud83c\udf9b\ufe0f",
  audio: "\ud83d\udd0a", sound: "\ud83c\udfb5", recording: "\ud83c\udf99\ufe0f",
  perform: "\ud83c\udfb9", scenario: "\ud83c\udfaf", live: "\ud83c\udfa4", common: "\ud83c\udfaf",
  home: "\ud83c\udfe0", studio: "\ud83c\udfa7", troubleshoot: "\ud83d\udd27",
  maintain: "\ud83e\uddf9", essential: "\u2705", recommend: "\ud83d\udc4d",
  overview: "\ud83d\udccb", checklist: "\u2705", getting_started: "\ud83d\ude80",
  first: "\ud83d\ude80", tip: "\ud83d\udca1", accessories: "\ud83c\udf92",
  advanced: "\ud83c\udfaf", basics: "\ud83d\udcd6",
};

/** Returns the appropriate icon for a section name. */
export function getSectionIcon(sectionName: string): string {
  const normalizedName = sectionName.toLowerCase().replace(/[\s-]/g, "_");
  for (const [pattern, icon] of Object.entries(SECTION_ICONS)) {
    if (normalizedName.includes(pattern)) return icon;
  }
  return "\u25b8";
}

/** Formats a label: underscores→spaces, camelCase split, title-cased. */
export function formatLabel(labelKey: string): string {
    return labelKey
        .replace(/_/g, " ")
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/\b\w/g, char => char.toUpperCase());
}

/** Returns true when value is a JS primitive (string | number | boolean). */
export function isPrimitive(value: unknown): value is string | number | boolean {
    return typeof value === "string" || typeof value === "number" || typeof value === "boolean";
}

/** Keys that might indicate a title field in a result object. */
export const TITLE_KEYS = new Set([
    "title", "scenarioName", "scenario_name", "name", "label",
    "instruction", "heading", "section_title", "sectionTitle",
]);

/** Keys that might indicate a tip/note field in a result object. */
export const TIP_KEYS = new Set([
    "tip", "tips", "pro_tip", "proTip", "pro_tips",
    "note", "notes", "warning", "caution", "important",
]);

/** Returns true when key matches a known tip/note pattern. */
export function isTipKey(key: string): boolean {
    return TIP_KEYS.has(key.toLowerCase().replace(/[\s-]/g, "_"));
}

/**
 * Extracts a title and its key from an object.
 * @returns [titleKey, titleValue] or [null, null] if not found.
 */
export function getTitleFromObj(obj: Record<string, unknown>): [string | null, string | null] {
    const key = Object.keys(obj).find(k => TITLE_KEYS.has(k));
    return key ? [key, String(obj[key])] : [null, null];
}
