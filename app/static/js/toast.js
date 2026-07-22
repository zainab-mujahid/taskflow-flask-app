(function () {
  function container() {
    var el = document.getElementById("toast-container");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast-container";
      el.className = "fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2 sm:bottom-6 sm:right-6";
      document.body.appendChild(el);
    }
    return el;
  }

  var ICONS = {
    success: '<svg class="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75l2.25 2.25 6-6"/><circle cx="12" cy="12" r="9" stroke="currentColor" fill="none"/></svg>',
    error: '<svg class="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m0 3.75h.008M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    info: '<svg class="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25h.75v5.25h.75M12 7.5h.008M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    warning: '<svg class="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/></svg>',
  };

  window.showToast = function (message, type) {
    type = ICONS[type] ? type : "info";
    var wrap = container();
    var toast = document.createElement("div");
    toast.className =
      "animate-slide-in-right flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4 shadow-lg dark:border-gray-700 dark:bg-gray-800";
    toast.innerHTML =
      '<div class="shrink-0">' + ICONS[type] + "</div>" +
      '<p class="flex-1 text-sm text-gray-700 dark:text-gray-200">' + message + "</p>" +
      '<button type="button" class="shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" aria-label="Dismiss">' +
      '<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg></button>';

    toast.querySelector("button").addEventListener("click", function () {
      toast.remove();
    });

    wrap.appendChild(toast);
    setTimeout(function () {
      toast.remove();
    }, 5000);
  };
})();
