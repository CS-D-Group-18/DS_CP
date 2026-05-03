import { Outlet, useLocation } from "react-router-dom";
import { Navbar } from "./Navbar";
import { motion, AnimatePresence } from "framer-motion";

export function Layout() {
  const location = useLocation();
  return (
    <div style={{ minHeight: "100vh", background: "#09090b" }}>
      <Navbar />
      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        >
          <Outlet />
        </motion.main>
      </AnimatePresence>
    </div>
  );
}
