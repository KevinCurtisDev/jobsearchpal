// Generates CSS custom properties from design/tokens.json.
// Usage: node scripts/build-tokens.mjs ../design/tokens.json src/styles/tokens.css
import { readFileSync, writeFileSync } from "node:fs";

const [, , input, output] = process.argv;
const t = JSON.parse(readFileSync(input, "utf8"));
const kebab = (s) => s.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();
const lines = [];
const add = (name, value) => lines.push(`  --${name}: ${value};`);

for (const [k, v] of Object.entries(t.color)) {
  if (v.value) add(`color-${kebab(k)}`, v.value);
}
for (const [k, v] of Object.entries(t.color.status)) {
  for (const [part, hex] of Object.entries(v))
    if (part !== "use") add(`status-${kebab(k)}-${part}`, hex);
}
for (const [k, v] of Object.entries(t.color.featureTint)) {
  for (const [part, hex] of Object.entries(v)) add(`tint-${k}-${part}`, hex);
}
add("font-family", t.font.family);
for (const [k, v] of Object.entries(t.font.scale)) {
  add(`font-${kebab(k)}-size`, `${v.size / 16}rem`);
  add(`font-${kebab(k)}-weight`, v.weight);
  add(`font-${kebab(k)}-tracking`, v.letterSpacing);
  add(`font-${kebab(k)}-leading`, v.lineHeight);
}
for (const [k, v] of Object.entries(t.space)) add(`space-${k}`, `${v}px`);
for (const [k, v] of Object.entries(t.radius)) add(`radius-${kebab(k)}`, `${v}px`);
for (const [k, v] of Object.entries(t.size)) add(`size-${kebab(k)}`, `${v}px`);
for (const [k, v] of Object.entries(t.shadow)) add(`shadow-${kebab(k)}`, v);

const css = `/* Generated from design/tokens.json by scripts/build-tokens.mjs. Do not edit by hand. */\n:root {\n${lines.join("\n")}\n}\n`;
writeFileSync(output, css);
console.log(`Wrote ${lines.length} tokens to ${output}`);
