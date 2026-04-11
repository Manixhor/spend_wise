(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var wrap = document.querySelector("[data-overview-chart]");
    if (!wrap) return;

    var hits = wrap.querySelectorAll(".dd-bar-hit");
    function clear() {
      wrap.classList.remove("is-hover");
    }

    hits.forEach(function (el) {
      el.addEventListener("mouseenter", function () {
        wrap.classList.add("is-hover");
      });
      el.addEventListener("mouseleave", clear);
      el.addEventListener("focus", function () {
        wrap.classList.add("is-hover");
      });
      el.addEventListener("blur", clear);
    });
  });
})();
