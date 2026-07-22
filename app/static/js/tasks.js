document.addEventListener("DOMContentLoaded", function () {
  // ---- Kanban drag & drop ----
  var columns = document.querySelectorAll(".kanban-column");
  var dragged = null;

  columns.forEach(function (column) {
    column.addEventListener("dragover", function (e) {
      e.preventDefault();
      var afterEl = getDragAfterElement(column, e.clientY);
      var list = column.querySelector(".kanban-list");
      if (!dragged || !list) return;
      if (afterEl == null) {
        list.appendChild(dragged);
      } else {
        list.insertBefore(dragged, afterEl);
      }
      column.classList.add("ring-2", "ring-primary-300");
    });
    column.addEventListener("dragleave", function () {
      column.classList.remove("ring-2", "ring-primary-300");
    });
    column.addEventListener("drop", function (e) {
      e.preventDefault();
      column.classList.remove("ring-2", "ring-primary-300");
      if (!dragged) return;
      var status = column.getAttribute("data-status");
      var list = column.querySelector(".kanban-list");
      var orderedIds = Array.prototype.map.call(
        list.querySelectorAll(".kanban-card"),
        function (card) { return parseInt(card.getAttribute("data-task-id"), 10); }
      );
      updateColumnCounts();
      apiFetch("/api/tasks/reorder", {
        method: "POST",
        body: JSON.stringify({ status: status, ordered_ids: orderedIds }),
      })
        .then(function (res) { return res.json(); })
        .then(function () {
          showToast("Task moved to " + column.getAttribute("data-label") + ".", "success");
        })
        .catch(function () {
          showToast("Could not update task. Please try again.", "error");
        });
    });
  });

  document.querySelectorAll(".kanban-card").forEach(function (card) {
    card.addEventListener("dragstart", function () {
      dragged = card;
      setTimeout(function () { card.classList.add("opacity-40"); }, 0);
    });
    card.addEventListener("dragend", function () {
      card.classList.remove("opacity-40");
      dragged = null;
      updateColumnCounts();
    });
  });

  function getDragAfterElement(column, y) {
    var list = column.querySelector(".kanban-list");
    if (!list) return null;
    var cards = Array.prototype.slice.call(list.querySelectorAll(".kanban-card:not(.opacity-40)"));
    return cards.reduce(function (closest, child) {
      var box = child.getBoundingClientRect();
      var offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      }
      return closest;
    }, { offset: Number.NEGATIVE_INFINITY, element: null }).element;
  }

  function updateColumnCounts() {
    columns.forEach(function (column) {
      var count = column.querySelectorAll(".kanban-card").length;
      var badge = column.querySelector(".kanban-count");
      if (badge) badge.textContent = count;
    });
  }

  // ---- Complete checkbox toggle (list view) ----
  document.querySelectorAll("[data-toggle-complete]").forEach(function (checkbox) {
    checkbox.addEventListener("change", function () {
      var taskId = checkbox.getAttribute("data-toggle-complete");
      var row = document.getElementById("task-row-" + taskId);
      apiFetch("/api/tasks/" + taskId + "/complete", {
        method: "PATCH",
        body: JSON.stringify({ is_completed: checkbox.checked }),
      })
        .then(function (res) { return res.json(); })
        .then(function () {
          if (row) row.classList.toggle("opacity-50", checkbox.checked);
          var title = row ? row.querySelector("[data-task-title]") : null;
          if (title) title.classList.toggle("line-through", checkbox.checked);
          showToast(checkbox.checked ? "Task marked complete." : "Task marked incomplete.", "success");
        })
        .catch(function () {
          showToast("Could not update task. Please try again.", "error");
        });
    });
  });
});
