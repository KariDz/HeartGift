/** Personalization lives only in public/config.json. */
export async function loadConfig() {
  const res = await fetch(new URL("./config.json", document.baseURI), { cache: "no-store" });
  if (!res.ok) throw new Error("Cannot load config.json (" + res.status + ")");
  const config = await res.json();
  if (!Array.isArray(config.photos) || !config.photos.length) throw new Error("config.photos must include at least one image");
  if (!config.letter || typeof config.letter.message !== "string") throw new Error("config.letter.message is required");
  return config;
}
export function assetUrl(path) {
  if (!path) return "";
  if (/^https?:\/\//.test(path) || path.startsWith("data:")) return path;
  return new URL(path.replace(/^\/+/, ""), document.baseURI).href;
}
