const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const navLinks = document.querySelector("[data-nav-links]");
const planLinks = document.querySelectorAll(".plan-link");
const planSelect = document.querySelector("#plan");
const form = document.querySelector("[data-lead-form]");
const successMessage = document.querySelector("[data-success-message]");

const updateHeader = () => {
  header.classList.toggle("is-scrolled", window.scrollY > 12);
};

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

menuToggle.addEventListener("click", () => {
  const isOpen = navLinks.classList.toggle("is-open");
  header.classList.toggle("menu-open", isOpen);
  menuToggle.setAttribute("aria-expanded", String(isOpen));
  menuToggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
});

navLinks.addEventListener("click", (event) => {
  if (event.target.matches("a")) {
    navLinks.classList.remove("is-open");
    header.classList.remove("menu-open");
    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Open menu");
  }
});

planLinks.forEach((link) => {
  link.addEventListener("click", () => {
    planSelect.value = link.dataset.plan;
    validateField(planSelect);
  });
});

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.16 }
);

document.querySelectorAll(".reveal").forEach((element) => revealObserver.observe(element));

const validators = {
  name: (value) => (value.trim() ? "" : "Full name is required."),
  email: (value) => {
    if (!value.trim()) return "Email address is required.";
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim()) ? "" : "Enter a valid email address.";
  },
  plan: (value) => (value ? "" : "Select a plan."),
  message: (value) => (value.trim() ? "" : "Message is required."),
};

function validateField(field) {
  const validator = validators[field.name];
  if (!validator) return true;

  const message = validator(field.value);
  const wrapper = field.closest(".field");
  const error = wrapper.querySelector(".error-message");
  wrapper.classList.toggle("has-error", Boolean(message));
  error.textContent = message;
  return !message;
}

form.querySelectorAll("input, select, textarea").forEach((field) => {
  field.addEventListener("input", () => {
    validateField(field);
    successMessage.textContent = "";
  });
  field.addEventListener("blur", () => validateField(field));
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const fields = Array.from(form.querySelectorAll("input, select, textarea"));
  const isValid = fields.map(validateField).every(Boolean);

  if (!isValid) {
    const firstError = form.querySelector(".has-error input, .has-error select, .has-error textarea");
    firstError?.focus();
    return;
  }

  form.reset();
  successMessage.textContent = "Thank you! We'll vibe with you within 24 hours.";
});
