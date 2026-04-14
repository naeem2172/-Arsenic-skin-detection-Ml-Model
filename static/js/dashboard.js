// Arsenic Detection Dashboard - Interactive scripts
(function () {
  function init() {
    var statEl = document.getElementById("stat-model");
    if (statEl && window.location.pathname === "/") {
      fetch("/api/status")
        .then(function (r) { return r.json(); })
        .then(function (data) {
          statEl.textContent = data.model_loaded ? "Loaded" : "Pending";
        })
        .catch(function () {});
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
