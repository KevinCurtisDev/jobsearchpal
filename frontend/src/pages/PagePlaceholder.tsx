import { Badge } from "../components/Badge";

interface Props {
  title: string;
  stage: string;
  spec: string;
}

/** Placeholder for screens not built yet. Replace with the real screen in the listed stage. */
export function PagePlaceholder({ title, stage, spec }: Props) {
  return (
    <section
      aria-labelledby="page-title"
      style={{ display: "flex", flexDirection: "column", gap: 12 }}
    >
      <h1
        id="page-title"
        style={{
          margin: 0,
          fontSize: "var(--font-title2-size)",
          letterSpacing: "var(--font-title2-tracking)",
        }}
      >
        {title}
      </h1>
      <p style={{ margin: 0 }}>
        <Badge tone="neutral">Built in {stage}</Badge>
      </p>
      <p style={{ margin: 0, color: "var(--color-graphite)" }}>Spec: {spec}</p>
    </section>
  );
}
