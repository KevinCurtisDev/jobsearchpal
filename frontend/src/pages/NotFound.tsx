import { Link } from "react-router";

export function NotFound() {
  return (
    <section aria-labelledby="nf-title" style={{ padding: 48 }}>
      <h1 id="nf-title">Page not found</h1>
      <p>
        <Link to="/">Go to the home page</Link>
      </p>
    </section>
  );
}
