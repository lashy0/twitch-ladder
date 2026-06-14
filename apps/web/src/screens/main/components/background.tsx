export function Background() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 overflow-hidden bg-black"
      style={{
        backgroundImage:
          "url(\"data:image/svg+xml;utf8,<svg viewBox='0 0 1920 1080' xmlns='http://www.w3.org/2000/svg' preserveAspectRatio='none'><rect x='0' y='0' height='100%' width='100%' fill='url(%23grad)' opacity='1'/><defs><radialGradient id='grad' gradientUnits='userSpaceOnUse' cx='0' cy='0' r='10' gradientTransform='matrix(-4.0924e-14 -108 383.59 5.8516e-7 960 1080)'><stop stop-color='rgba(146,71,255,1)' offset='0.14904'/><stop stop-color='rgba(110,53,191,1)' offset='0.23678'/><stop stop-color='rgba(91,44,159,1)' offset='0.28065'/><stop stop-color='rgba(73,36,128,1)' offset='0.32452'/><stop stop-color='rgba(55,27,96,1)' offset='0.36839'/><stop stop-color='rgba(37,18,64,1)' offset='0.41226'/><stop stop-color='rgba(18,9,32,1)' offset='0.45613'/><stop stop-color='rgba(9,4,16,1)' offset='0.47806'/><stop stop-color='rgba(0,0,0,1)' offset='0.5'/></radialGradient></defs></svg>\")",
        backgroundSize: "100% 100%",
      }}
    >
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
