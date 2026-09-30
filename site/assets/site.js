// Catalogue search (home page) and literature filters (research page). No dependencies.
(function () {
  var q = document.getElementById("q");
  if (q) {
    var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
    var topics = Array.prototype.slice.call(document.querySelectorAll(".topic"));
    var status = document.getElementById("q-status");
    var run = function () {
      var terms = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      var shown = 0;
      cards.forEach(function (c) {
        var hay = c.getAttribute("data-search");
        var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; });
        c.hidden = !ok;
        if (ok) shown++;
      });
      topics.forEach(function (t) { t.hidden = !t.querySelector(".card:not([hidden])"); });
      status.textContent = terms.length ? shown + " of " + cards.length + " datasets match" : "";
    };
    q.addEventListener("input", run);
    var params = new URLSearchParams(location.search);
    if (params.get("q")) { q.value = params.get("q"); run(); }
  }

  var dataEl = document.getElementById("lit-data");
  if (dataEl) {
    var recs = JSON.parse(dataEl.textContent);
    var list = document.getElementById("lit");
    var count = document.getElementById("lcount");
    var f = {
      q: document.getElementById("lq"), t: document.getElementById("lt"),
      e: document.getElementById("le"), y: document.getElementById("ly")
    };
    var esc = function (s) {
      return String(s).replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    };
    recs.forEach(function (r) {
      r._hay = [r.title, r.authors, r.abstract, r.venue, r.publisher, r.data_sources].join(" ").toLowerCase();
    });
    var render = function () {
      var terms = f.q.value.toLowerCase().split(/\s+/).filter(Boolean);
      var out = recs.filter(function (r) {
        return (!f.t.value || r.primary_theme === f.t.value) &&
          (!f.e.value || r.evidence_type === f.e.value) &&
          (!f.y.value || r.year === f.y.value) &&
          terms.every(function (t) { return r._hay.indexOf(t) !== -1; });
      });
      count.textContent = out.length + " of " + recs.length + " publications";
      list.innerHTML = out.map(function (r) {
        var link = r.url || (r.doi ? "https://doi.org/" + r.doi : "");
        var title = link ? '<a href="' + esc(link) + '">' + esc(r.title) + "</a>" : esc(r.title);
        var venue = r.venue || r.publisher;
        var tags = [r.primary_theme, r.evidence_type, r.publication_type].filter(Boolean)
          .map(function (t) { return '<span class="tag">' + esc(t) + "</span>"; }).join("");
        var ft = r.full_text ? ' · <a href="' + esc(r.full_text) + '">full text</a>' : "";
        var abs = r.abstract ? "<details><summary>Abstract</summary><p>" + esc(r.abstract) + "</p></details>" : "";
        return "<li><h3>" + title + "</h3><p class=\"meta\">" + esc(r.authors) + " (" + esc(r.year) + ")" +
          (venue ? ". <em>" + esc(venue) + "</em>" : "") + ft + "</p><p>" + tags + "</p>" + abs + "</li>";
      }).join("");
    };
    [f.q, f.t, f.e, f.y].forEach(function (el) { el.addEventListener("input", render); });
    render();
  }
})();
