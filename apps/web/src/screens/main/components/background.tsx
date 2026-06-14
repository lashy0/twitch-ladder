const gradientBackground = [
  "radial-gradient(ellipse 199.79% 100% at 50% 100%,",
  "#9247ff 14.904%,",
  "#6e35bf 23.678%,",
  "#5b2c9f 28.065%,",
  "#492480 32.452%,",
  "#371b60 36.839%,",
  "#251240 41.226%,",
  "#120920 45.613%,",
  "#090410 47.806%,",
  "#000 50%)",
].join(" ");

export function Background() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 overflow-hidden bg-black"
    >
      <div
        className="absolute left-1/2 top-1/2 min-h-full w-full min-w-[177.777778vh] -translate-x-1/2 -translate-y-1/2"
        style={{
          aspectRatio: "16 / 9",
          backgroundImage: gradientBackground,
        }}
      />

      <div
        className="absolute inset-0 backdrop-blur-[400px]"
        style={{ background: "rgba(217, 217, 217, 0.01)" }}
      />

      <div
        className="absolute inset-0 mix-blend-multiply"
        style={{ background: "rgba(255, 255, 255, 0.2)" }}
      />

      <div
        className="absolute inset-0"
        style={{ background: "rgba(0, 0, 0, 0.65)" }}
      />
    </div>
  );
}
