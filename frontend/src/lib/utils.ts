// Since clsx and tailwind-merge are not in package.json, we use a simple fallback
// If you add them later, uncomment the imports above and use this:
// export function cn(...inputs: ClassValue[]) {
//   return twMerge(clsx(inputs));
// }

export function cn(...inputs: (string | undefined | null | false)[]) {
  return inputs.filter(Boolean).join(" ");
}
