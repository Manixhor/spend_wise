(function () {
  "use strict";

  var MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];

  function parseStart(label) {
    var raw = label.getAttribute("data-range-start");
    if (!raw) return null;
    var d = new Date(raw + "T12:00:00");
    return Number.isNaN(d.getTime()) ? null : d;
  }

  function formatRange(start, end) {
    var d1 = start.getDate();
    var d2 = end.getDate();
    var m1 = start.getMonth();
    var m2 = end.getMonth();
    var y1 = start.getFullYear();
    var y2 = end.getFullYear();
    if (m1 === m2 && y1 === y2) {
      return d1 + "–" + d2 + " " + MONTHS[m1] + " " + y1;
    }
    return d1 + " " + MONTHS[m1] + " – " + d2 + " " + MONTHS[m2] + " " + y2;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var prev = document.querySelector("[data-date-prev]");
    var next = document.querySelector("[data-date-next]");
    var label = document.querySelector("[data-date-label]");

    function bump(days) {
      if (!label) return;
      var start = parseStart(label);
      if (!start) return;
      start.setDate(start.getDate() + days);
      var end = new Date(start);
      end.setDate(end.getDate() + 6);
      label.textContent = formatRange(start, end);
      label.setAttribute("data-range-start", start.toISOString().slice(0, 10));
    }

    if (prev) prev.addEventListener("click", function () { bump(-7); });
    if (next) next.addEventListener("click", function () { bump(7); });
  });
})();
