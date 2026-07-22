document.addEventListener("DOMContentLoaded", function () {
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("sidebar-overlay");
  var openBtn = document.getElementById("sidebar-open");
  var closeBtn = document.getElementById("sidebar-close");

  function openSidebar() {
    sidebar && sidebar.classList.remove("-translate-x-full");
    overlay && overlay.classList.remove("hidden");
  }
  function closeSidebar() {
    sidebar && sidebar.classList.add("-translate-x-full");
    overlay && overlay.classList.add("hidden");
  }
  openBtn && openBtn.addEventListener("click", openSidebar);
  closeBtn && closeBtn.addEventListener("click", closeSidebar);
  overlay && overlay.addEventListener("click", closeSidebar);

  var themeToggle = document.getElementById("theme-toggle");
  themeToggle &&
    themeToggle.addEventListener("click", function () {
      window.TaskFlowTheme.toggle();
    });

  document.querySelectorAll("[data-dropdown-toggle]").forEach(function (btn) {
    var target = document.getElementById(btn.getAttribute("data-dropdown-toggle"));
    if (!target) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      document.querySelectorAll(".dropdown-menu").forEach(function (menu) {
        if (menu !== target) menu.classList.add("hidden");
      });
      target.classList.toggle("hidden");
    });
  });
  document.addEventListener("click", function () {
    document.querySelectorAll(".dropdown-menu").forEach(function (menu) {
      menu.classList.add("hidden");
    });
  });

  document.querySelectorAll("[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!confirm(form.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });

  window.__FLASHED_MESSAGES__ &&
    window.__FLASHED_MESSAGES__.forEach(function (m) {
      showToast(m[1], m[0] === "error" ? "error" : m[0]);
    });
});
