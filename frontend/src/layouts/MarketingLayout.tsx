import { Link, Outlet } from "react-router";
import { LogoMark } from "../components/Logo";

export function MarketingLayout() {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <header style={{ borderBottom: "1px solid var(--color-hairline)" }}>
        <div
          style={{
            maxWidth: "var(--size-content-max)",
            margin: "0 auto",
            padding: "0 24px",
            minHeight: 64,
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          <Link
            to="/"
            aria-label="Offerlight home"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              color: "var(--color-ink)",
              fontWeight: 600,
            }}
          >
            <LogoMark size={28} /> Offerlight
          </Link>
          <nav aria-label="Primary" style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            <Link to="/sign-in">Sign in</Link>
            <Link to="/sign-up">Start free</Link>
          </nav>
        </div>
      </header>
      <main id="main">
        <Outlet />
      </main>
      <footer
        style={{
          padding: "48px 24px",
          background: "var(--color-mist)",
          fontSize: "var(--font-footnote-size)",
        }}
      >
        <p
          style={{
            maxWidth: "var(--size-content-max)",
            margin: "0 auto",
            color: "var(--color-slate)",
          }}
        >
          Offerlight is a working name.
        </p>
      </footer>
    </>
  );
}
