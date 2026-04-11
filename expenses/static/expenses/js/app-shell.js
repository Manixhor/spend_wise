(function () {
  "use strict";

  var sidebar = document.getElementById("sidebar");
  var backdrop = document.getElementById("sidebarBackdrop");
  var openBtn = document.getElementById("menuOpen");
  var closeBtn = document.getElementById("sidebarClose");

  function isDesktop() {
    return window.matchMedia("(min-width: 960px)").matches;
  }

  function openSidebar() {
    if (!sidebar || !backdrop) return;
    sidebar.classList.add("is-open");
    backdrop.classList.add("is-visible");
    if (openBtn) openBtn.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  function closeSidebar() {
    if (!sidebar || !backdrop) return;
    sidebar.classList.remove("is-open");
    backdrop.classList.remove("is-visible");
    if (openBtn) openBtn.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }

  function toggleSidebar() {
    if (sidebar && sidebar.classList.contains("is-open")) {
      closeSidebar();
    } else {
      openSidebar();
    }
  }

  if (openBtn) {
    openBtn.addEventListener("click", function () {
      toggleSidebar();
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      closeSidebar();
    });
  }

  if (backdrop) {
    backdrop.addEventListener("click", function () {
      closeSidebar();
    });
  }

  window.addEventListener(
    "keydown",
    function (e) {
      if (e.key === "Escape") closeSidebar();
    },
    { passive: true }
  );

  window.addEventListener(
    "resize",
    function () {
      if (isDesktop()) closeSidebar();
    },
    { passive: true }
  );
})();
