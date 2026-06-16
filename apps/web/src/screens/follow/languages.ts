const languageNames = new Intl.DisplayNames(["ru"], { type: "language" });

export function languageLabel(language: string) {
  const code = language.trim().replace("_", "-");
  if (!code || code.toUpperCase() === "OTHER") return "Другой";

  const label = languageNames.of(code.toLowerCase());
  return label ? capitalize(label) : code.toUpperCase();
}

export function languageEmoji(language: string) {
  const code = language.trim().replace("_", "-");
  if (!code || code.toUpperCase() === "OTHER") return "🌐";

  try {
    const region = new Intl.Locale(code.toLowerCase()).maximize().region;
    return region ? regionToFlag(region) : "🌐";
  } catch {
    return "🌐";
  }
}

function capitalize(value: string) {
  return value.charAt(0).toLocaleUpperCase("ru-RU") + value.slice(1);
}

function regionToFlag(region: string) {
  const code = region.toUpperCase();
  if (!/^[A-Z]{2}$/.test(code)) return "🌐";

  return [...code]
    .map((letter) => String.fromCodePoint(0x1f1e6 + letter.charCodeAt(0) - 65))
    .join("");
}
