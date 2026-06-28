// Alvia — drobna interaktywność strony one-page

document.addEventListener("DOMContentLoaded", () => {
  // Aktualny rok w stopce
  const yearEl = document.querySelector("[data-year]");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Menu mobilne
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    // Zamknij menu po kliknięciu w link
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Formularz poglądowy — bez backendu pokazuje komunikat
  const form = document.querySelector(".contact-form");
  const note = document.querySelector("[data-form-note]");
  if (form && note) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      note.hidden = false;
      form.reset();
    });
  }
});
