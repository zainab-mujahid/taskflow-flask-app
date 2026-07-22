(function () {
  function getCsrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : null;
  }

  window.apiFetch = function (url, options) {
    options = options || {};
    options.credentials = "same-origin";
    options.headers = options.headers || {};

    var method = (options.method || "GET").toUpperCase();
    if (method !== "GET") {
      var csrf = getCsrfToken();
      if (csrf) options.headers["X-CSRF-TOKEN"] = csrf;
    }
    if (options.body && !(options.body instanceof FormData) && !options.headers["Content-Type"]) {
      options.headers["Content-Type"] = "application/json";
    }

    return fetch(url, options).then(function (res) {
      if (res.status === 401) {
        window.location.href = "/auth/login?next=" + encodeURIComponent(window.location.pathname);
        throw new Error("Unauthenticated");
      }
      return res;
    });
  };
})();
