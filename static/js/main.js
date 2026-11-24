document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-copy]");
  if (!btn) return;
  const sel = btn.getAttribute("data-copy");
  const el = document.querySelector(sel);
  if (!el) return;
  const text = el.innerText || el.value || "";
  navigator.clipboard.writeText(text).then(() => {
    const old = btn.innerText;
    btn.innerText = "کپی شد";
    setTimeout(() => (btn.innerText = old), 1500);
  });
});