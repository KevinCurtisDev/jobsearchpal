import clsx from "clsx";
import type { ReactNode } from "react";
import styles from "./Badge.module.css";

export type BadgeTone = "positive" | "caution" | "critical" | "info" | "criticalSkills" | "neutral";

/** Status badge: always words (and usually an icon) — never colour alone. */
export function Badge({
  tone,
  icon,
  children,
}: {
  tone: BadgeTone;
  icon?: ReactNode;
  children: ReactNode;
}) {
  return (
    <span className={clsx(styles.badge, styles[tone])}>
      {icon ? <span aria-hidden="true">{icon}</span> : null}
      {children}
    </span>
  );
}
