import clsx from "clsx";
import type { ButtonHTMLAttributes } from "react";
import styles from "./Button.module.css";

export type ButtonVariant = "primary" | "secondary" | "tertiary" | "danger";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: "md" | "lg";
}

/** Pill button. One primary per view. Icon-only buttons must pass aria-label. */
export function Button({
  variant = "primary",
  size = "md",
  className,
  type = "button",
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={clsx(styles.button, styles[variant], size === "lg" && styles.lg, className)}
      {...rest}
    />
  );
}
