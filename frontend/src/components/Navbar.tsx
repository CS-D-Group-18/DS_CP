import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Zap } from "lucide-react";

const NAV_LINKS = [
  { label: "DASHBOARD", href: "/" },
  { label: "TASKS", href: "/tasks" },
  { label: "DEPENDENCIES", href: "/dependencies" },
  { label: "SCHEDULER", href: "/scheduler" },
  { label: "ANALYTICS", href: "/analytics" },
  { label: "LOGS", href: "/logs" },
  { label: "REPORTS", href: "/reports" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => { setMenuOpen(false); }, [location]);

  return (
    <>
      <nav
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
        style={{
          background: scrolled ? "rgba(9,9,11,0.95)" : "transparent",
          backdropFilter: scrolled ? "blur(12px)" : "none",
          borderBottom: scrolled ? "1px solid #27272a" : "none",
        }}
      >
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110"
              style={{ background: "#6366f1" }}
            >
              <Zap size={16} style={{ color: "#09090b" }} fill="currentColor" />
            </div>
            <span className="text-lg font-black tracking-tight" style={{ color: "#fafafa" }}>
              task<span style={{ color: "#6366f1" }}>flow</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map(({ label, href }) => {
              const isActive = href === "/" ? location.pathname === "/" : location.pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  to={href}
                  className="text-xs font-bold tracking-widest transition-colors duration-200"
                  style={{ color: isActive ? "#6366f1" : "#71717a" }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = "#6366f1")}
                  onMouseLeave={(e) => (e.currentTarget.style.color = isActive ? "#6366f1" : "#71717a")}
                >
                  {label}
                </Link>
              );
            })}
          </div>

          {/* CTA */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              to="/settings"
              className="text-xs font-bold tracking-widest transition-colors"
              style={{ color: "#71717a" }}
            >
              SETTINGS
            </Link>
            <Link
              to="/scheduler"
              className="px-5 py-2 rounded-full text-xs font-black tracking-widest transition-all active:scale-95"
              style={{ background: "#6366f1", color: "#fafafa" }}
            >
              RUN SCHEDULER
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-lg transition-colors"
            style={{ color: "#fafafa" }}
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            className="fixed inset-0 z-40 flex flex-col pt-16"
            style={{ background: "rgba(9,9,11,0.98)" }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex flex-col items-center justify-center flex-1 gap-8">
              {NAV_LINKS.map(({ label, href }) => (
                <Link
                  key={href}
                  to={href}
                  className="text-2xl font-black tracking-widest"
                  style={{ color: "#fafafa" }}
                >
                  {label}
                </Link>
              ))}
              <Link
                to="/scheduler"
                className="mt-4 px-8 py-3 rounded-full text-sm font-black tracking-widest"
                style={{ background: "#6366f1", color: "#fafafa" }}
              >
                RUN SCHEDULER
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
