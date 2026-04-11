(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var page = document.querySelector(".page");
    if (page) {
      page.classList.add("page--ready");
    }
  });
})();
