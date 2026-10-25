/* The Supported vehicles page: filter the profile list as you type, and the
   make chips as one-click filters. Nothing here is needed to read the page:
   without scripts every profile is listed. */
(function () {
  function init() {
    var box = document.getElementById("veh-filter");
    if (!box) return;
    var rows = Array.prototype.slice.call(document.querySelectorAll("tr[data-text]"));
    var heads = Array.prototype.slice.call(document.querySelectorAll("tr.veh-make"));
    var chips = Array.prototype.slice.call(document.querySelectorAll(".veh-chip"));
    var count = document.getElementById("veh-count");
    var empty = document.getElementById("veh-empty");
    var total = Number(count.getAttribute("data-total"));
    var makes = Number(count.getAttribute("data-makes"));
    var activeMake = null;

    function apply() {
      var words = box.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      var shown = 0;
      var shownMakes = {};
      rows.forEach(function (r) {
        var text = r.getAttribute("data-text");
        var make = r.getAttribute("data-make");
        var ok = (!activeMake || make === activeMake) && words.every(function (w) { return text.indexOf(w) >= 0; });
        r.hidden = !ok;
        if (ok) { shown++; shownMakes[make] = true; }
      });
      heads.forEach(function (h) { h.hidden = !shownMakes[h.getAttribute("data-make")]; });
      chips.forEach(function (c) {
        var m = c.getAttribute("data-make");
        c.classList.toggle("is-on", m === activeMake);
        c.classList.toggle("is-dim", (words.length > 0 || !!activeMake) && !shownMakes[m]);
      });
      var n = Object.keys(shownMakes).length;
      var filtering = words.length > 0 || !!activeMake;
      count.textContent = filtering
        ? shown + " of " + total + " profiles, " + n + (n === 1 ? " make" : " makes")
        : total + " profiles, " + makes + " makes";
      empty.hidden = shown > 0;
    }

    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        var m = c.getAttribute("data-make");
        activeMake = activeMake === m ? null : m;
        apply();
        if (activeMake) {
          var head = heads.filter(function (h) { return h.getAttribute("data-make") === m; })[0];
          if (head && head.scrollIntoView) head.scrollIntoView({ block: "start", behavior: "smooth" });
        }
      });
    });
    box.addEventListener("input", apply);
    box.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { box.value = ""; activeMake = null; apply(); }
    });
    apply();
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(init);
  } else if (document.readyState !== "loading") {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
