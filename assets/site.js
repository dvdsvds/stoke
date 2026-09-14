document.querySelectorAll(".side-group").forEach(function (group) {
  var btn = group.querySelector(".side-group-toggle");
  var list = group.querySelector(".side-group-list");
  if (!btn || !list) return;

  // Set an exact starting max-height (instead of the CSS default's generous
  // 1000px cap) so the very first toggle animates over the real distance,
  // not however much of the 1000px range happens to matter.
  list.style.maxHeight = group.classList.contains("expanded")
    ? list.scrollHeight + "px"
    : "0px";

  btn.addEventListener("click", function () {
    var expanding = !group.classList.contains("expanded");
    if (expanding) {
      group.classList.add("expanded");
      list.style.maxHeight = list.scrollHeight + "px";
    } else {
      // Force the current (measured) height first so the transition has a
      // real starting point instead of jumping from "auto"/1000px.
      list.style.maxHeight = list.scrollHeight + "px";
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          list.style.maxHeight = "0px";
        });
      });
      group.classList.remove("expanded");
    }
  });
});

(function () {
  var input = document.getElementById("site-search");
  var resultsBox = document.getElementById("search-results");
  if (!input || !resultsBox) return;

  var root = document.body.dataset.root || "";
  var lang = document.body.dataset.lang || "en";
  var index = null;

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function loadIndex() {
    if (index) return Promise.resolve(index);
    return fetch(root + "assets/search-index." + lang + ".json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; return data; });
  }

  function render(matches) {
    if (!matches.length) {
      resultsBox.innerHTML = '<div class="search-empty">' + (lang === "ko" ? "결과 없음" : "No results") + "</div>";
      resultsBox.hidden = false;
      return;
    }
    resultsBox.innerHTML = matches
      .slice(0, 8)
      .map(function (m) {
        return (
          '<a href="' + root + m.url + '">' +
          '<span class="sr-title">' + escapeHtml(m.title) + "</span>" +
          '<span class="sr-excerpt">' + escapeHtml(m.excerpt) + "</span>" +
          "</a>"
        );
      })
      .join("");
    resultsBox.hidden = false;
  }

  input.addEventListener("input", function () {
    var q = input.value.trim().toLowerCase();
    if (!q) {
      resultsBox.hidden = true;
      return;
    }
    loadIndex().then(function (data) {
      var matches = data.filter(function (item) {
        return (
          item.title.toLowerCase().indexOf(q) !== -1 ||
          item.excerpt.toLowerCase().indexOf(q) !== -1
        );
      });
      render(matches);
    });
  });

  input.addEventListener("focus", function () {
    if (input.value.trim()) input.dispatchEvent(new Event("input"));
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      resultsBox.hidden = true;
      input.blur();
    }
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav-search")) resultsBox.hidden = true;
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== input) {
      var tag = (document.activeElement && document.activeElement.tagName) || "";
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      e.preventDefault();
      input.focus();
    }
  });
})();
