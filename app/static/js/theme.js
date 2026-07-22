(function () {
  function applyTheme(theme) {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }

  var stored = localStorage.getItem("theme");
  applyTheme(stored || "light");

  window.TaskFlowTheme = {
    toggle: function () {
      var current = localStorage.getItem("theme") === "dark" ? "dark" : "light";
      var next = current === "dark" ? "light" : "dark";
      localStorage.setItem("theme", next);
      applyTheme(next);

      if (window.apiFetch) {
        window.apiFetch("/profile/theme", {
          method: "POST",
          body: JSON.stringify({ theme: next }),
        }).catch(function () {});
      }

      return next;
    },
    current: function () {
      return localStorage.getItem("theme") === "dark" ? "dark" : "light";
    },
  };
})();
