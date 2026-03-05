// Joyforest main interactions

document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.querySelector(".nav-toggle");
  const navMain = document.querySelector(".nav-main");

  // Mobile nav toggle
  if (navToggle && navMain) {
    navToggle.addEventListener("click", () => {
      navMain.classList.toggle("is-open");
      const expanded = navToggle.getAttribute("aria-expanded") === "true";
      navToggle.setAttribute("aria-expanded", String(!expanded));
    });
  }

  // Close mobile nav when clicking a link
  if (navMain) {
    navMain.addEventListener("click", (event) => {
      const target = event.target;
      if (target instanceof HTMLAnchorElement && navMain.classList.contains("is-open")) {
        navMain.classList.remove("is-open");
        if (navToggle) {
          navToggle.setAttribute("aria-expanded", "false");
        }
      }
    });
  }

  // Smooth scroll for in-page anchors (non-external)
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (event) => {
      const href = (event.currentTarget as HTMLAnchorElement).getAttribute("href");
      if (!href || href === "#" || href.startsWith("#!") || href.length <= 1) return;

      const target = document.querySelector(href);
      if (target) {
        event.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
});

