import { Link } from "react-router";

/** Stage 4 builds the full landing page (docs/08-screens.md §Marketing site). */
export function Landing() {
  return (
    <section
      aria-labelledby="hero-title"
      style={{ padding: "96px 24px 72px", textAlign: "center" }}
    >
      <h1
        id="hero-title"
        style={{
          margin: "0 auto",
          maxWidth: 920,
          fontSize: "clamp(2.5rem, 6vw, var(--font-display-size))",
          lineHeight: "var(--font-display-leading)",
          letterSpacing: "var(--font-display-tracking)",
        }}
      >
        Built for <span style={{ color: "var(--color-accent)" }}>offers received</span>, not
        applications submitted.
      </h1>
      <p
        style={{
          margin: "24px auto 0",
          maxWidth: 660,
          fontSize: "1.375rem",
          color: "var(--color-graphite)",
        }}
      >
        A CV that passes screening, jobs worth your time, and honest evidence of what gets you
        hired.
      </p>
      <p style={{ marginTop: 32 }}>
        <Link to="/sign-up">Start free</Link>
      </p>
    </section>
  );
}
