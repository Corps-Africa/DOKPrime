/* =========================================================
   DOK Prime Ventures: site script
   Products, WhatsApp links and contact details are filled in
   at build time (see build.py and src/data/). This file only
   handles small interactions.
   ========================================================= */

/* ---- Mobile navigation ---- */
function initNav() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (!toggle || !nav) return;

  const setOpen = (open) => {
    toggle.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("open", open);
  };
  toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
  nav.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setOpen(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
}

/* ---- Products page: highlight the section in view ---- */
function initSectionTabs() {
  const links = document.querySelectorAll(".jump-nav a");
  if (!links.length || !("IntersectionObserver" in window)) return;
  const byId = new Map([...links].map((a) => [a.hash.slice(1), a]));
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) {
        links.forEach((a) => a.classList.remove("active"));
        byId.get(en.target.id)?.classList.add("active");
      }
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  byId.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
}

/* ---- Contact form ---- */
function initContactForm() {
  const form = document.getElementById("enquiry-form");
  if (!form) return;
  const status = form.querySelector(".form-status");

  const show = (msg, kind) => {
    status.textContent = msg;
    status.className = `form-status ${kind}`;
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }

    if (form.action.includes("YOUR_FORM_ID")) {
      show("Preview only: the form isn't connected yet. Please contact us on WhatsApp for now.", "warn");
      return;
    }

    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    show("Sending…", "info");
    try {
      const res = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(res.statusText);
      form.reset();
      show("Thank you! Your message has been sent. We'll get back to you soon.", "ok");
    } catch {
      show("Sorry, something went wrong. Please try again or message us on WhatsApp.", "error");
    } finally {
      btn.disabled = false;
    }
  });
}

/* ---- Init ---- */
document.addEventListener("DOMContentLoaded", () => {
  initNav();
  initSectionTabs();
  initContactForm();
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
});
