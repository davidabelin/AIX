// AIX hub: category filter chips for the lab grid.
// Progressive enhancement: without JS every card stays visible and the chips stay hidden.
(function () {
  "use strict";

  var bar = document.querySelector("[data-filter-bar]");
  if (!bar) {
    return;
  }
  var chips = Array.prototype.slice.call(bar.querySelectorAll("[data-filter]"));
  var cards = Array.prototype.slice.call(document.querySelectorAll(".lab-card[data-category]"));
  var empty = document.querySelector("[data-filter-empty]");
  var storageKey = "aix-hub-filter";

  function apply(filter) {
    var shown = 0;
    cards.forEach(function (card) {
      var match = filter === "all" || card.getAttribute("data-category") === filter;
      card.hidden = !match;
      if (match) {
        shown += 1;
      }
    });
    chips.forEach(function (chip) {
      chip.setAttribute("aria-pressed", chip.getAttribute("data-filter") === filter ? "true" : "false");
    });
    if (empty) {
      empty.hidden = shown > 0;
    }
    try {
      window.sessionStorage.setItem(storageKey, filter);
    } catch (err) {
      // Storage can be unavailable (private mode, blocked site data); filtering still works.
    }
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      apply(chip.getAttribute("data-filter"));
    });
  });

  var initial = "all";
  try {
    initial = window.sessionStorage.getItem(storageKey) || "all";
  } catch (err) {
    initial = "all";
  }
  var known = chips.some(function (chip) {
    return chip.getAttribute("data-filter") === initial;
  });
  bar.hidden = false;
  apply(known ? initial : "all");
})();
