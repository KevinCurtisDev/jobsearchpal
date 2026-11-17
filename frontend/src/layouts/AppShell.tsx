import { NavLink, Outlet } from "react-router";
import { LogoMark } from "../components/Logo";
import styles from "./AppShell.module.css";

export const APP_NAV = [
  { to: "/app", label: "Home", end: true },
  { to: "/app/cv", label: "CV builder" },
  { to: "/app/tailor", label: "Tailor to a job" },
  { to: "/app/linkedin", label: "LinkedIn profile" },
  { to: "/app/jobs", label: "Job matches" },
  { to: "/app/applications", label: "Applications" },
  { to: "/app/insights", label: "What works" },
  { to: "/app/interviews", label: "Interviews & offers" },
  { to: "/app/settings", label: "Privacy & settings" },
] as const;

/** App layout: skip link, side nav (stacks above content on small screens), main region. */
export function AppShell() {
  return (
    <div className={styles.shell}>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <nav aria-label="Main" className={styles.nav}>
        <NavLink to="/" className={styles.brand} aria-label="Offerlight home">
          <LogoMark /> Offerlight
        </NavLink>
        {APP_NAV.map((item) => (
          <NavLink key={item.to} to={item.to} end={"end" in item} className={styles.link}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className={styles.content}>
        <main id="main" className={styles.main}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
