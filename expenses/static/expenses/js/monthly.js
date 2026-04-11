(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var line = document.querySelector(".chart-line");
    if (!line || typeof line.getTotalLength !== "function") return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      line.style.strokeDasharray = "none";
      line.style.strokeDashoffset = "0";
      return;
    }

    var len = line.getTotalLength();
    line.style.strokeDasharray = String(len);
    line.style.strokeDashoffset = String(len);

    requestAnimationFrame(function () {
      line.classList.add("is-drawn");
      line.style.strokeDashoffset = "0";
    });
  });
})();
