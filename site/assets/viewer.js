// Data viewer for dataset pages: loads the whole CSV (or JSON) file in the browser
// and shows it with search, a drop-down filter per column, sorting and paging.
// The page is rendered with the first rows already, so it still works without this.
(function () {
  var box = document.getElementById("viewer");
  if (!box) return;
  var PAGE = 100, MAX_OPTIONS = 300;
  var status = document.getElementById("v-status");
  status.textContent = "Loading all rows" + (box.getAttribute("data-size") ? " (" + box.getAttribute("data-size") + ")" : "") + "…";

  var esc = function (s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  };
  var isNum = function (v) { return v !== "" && !isNaN(v.replace(/,/g, "")); };
  var num = function (v) { return parseFloat(v.replace(/,/g, "")); };

  fetch(box.getAttribute("data-src"))
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
    .then(function (text) {
      var header, rows;
      if (box.getAttribute("data-format") === "json") {
        var items = JSON.parse(text).filter(function (o) { return o && typeof o === "object"; });
        header = [];
        items.forEach(function (o) { Object.keys(o).forEach(function (k) { if (header.indexOf(k) < 0) header.push(k); }); });
        rows = items.map(function (o) {
          return header.map(function (k) {
            var v = o[k];
            return v == null ? "" : typeof v === "object" ? JSON.stringify(v) : String(v);
          });
        });
      } else {
        var parsed = Papa.parse(text.replace(/^﻿/, ""), { skipEmptyLines: true });
        header = parsed.data[0];
        rows = parsed.data.slice(1);
      }
      setup(header, rows);
    })
    .catch(function (e) {
      status.textContent = "Could not load the whole file (" + e.message + "). The first rows are shown below; download the file for the rest.";
    });

  function setup(header, rows) {
    var n = header.length;
    // Profile columns: distinct values (for filters), numeric (for sorting and alignment).
    var cols = header.map(function (name, i) {
      var seen = new Map(), numeric = 0, filled = 0;
      for (var r = 0; r < rows.length; r++) {
        var v = rows[r][i] == null ? "" : rows[r][i];
        if (v !== "") { filled++; if (isNum(v)) numeric++; }
        if (seen && seen.size <= MAX_OPTIONS) seen.set(v, (seen.get(v) || 0) + 1);
        else seen = null;
      }
      var long = 0;
      for (var k = 0; k < Math.min(rows.length, 200); k++) long += (rows[k][i] || "").length;
      return { name: name, i: i, values: seen, numeric: filled > 0 && numeric / filled > 0.9,
               long: long / Math.max(1, Math.min(rows.length, 200)) > 60 };
    });
    // Columns with one value in every row are shown once above the table, not in it.
    var constant = cols.filter(function (c) { return rows.length > 1 && c.values && c.values.size === 1; });
    var shown = cols.filter(function (c) { return constant.indexOf(c) < 0; });
        // Drop-down filters for categories and years, not for counts or free text.
    var filterable = shown.filter(function (c) {
      return c.values && c.values.size > 1 && c.values.size <= MAX_OPTIONS && c.name !== "view" && !c.long &&
        (!c.numeric || /year|quarter|^time$/i.test(c.name));
    });

    var state = { q: "", filters: {}, sort: null, dir: 1, page: 0 };
    var lower = null;

    var sortOpts = function (c) {
      var vals = Array.from(c.values.keys());
      return c.numeric ? vals.sort(function (a, b) { return (num(a) || 0) - (num(b) || 0); }) : vals.sort();
    };
    var controls = '<div class="v-controls"><label class="v-search">Search all columns' +
      '<input type="search" id="v-q" placeholder="e.g. India 2024" autocomplete="off"></label>' +
      filterable.map(function (c) {
        return '<label>' + esc(c.name) + '<select data-col="' + c.i + '"><option value="">All (' + c.values.size + ')</option>' +
          sortOpts(c).map(function (v) {
            return '<option value="' + esc(v) + '">' + esc(v === "" ? "(blank)" : v.length > 60 ? v.slice(0, 60) + "…" : v) + '</option>';
          }).join("") + '</select></label>';
      }).join("") + '</div>';
    var fixed = constant.length
      ? '<p class="small v-fixed">Same in every row: ' + constant.map(function (c) {
          return '<span><b>' + esc(c.name) + '</b>: ' + esc(Array.from(c.values.keys())[0]) + '</span>';
        }).join(" · ") + '</p>'
      : "";
    box.innerHTML = controls + fixed +
      '<div class="v-bar"><span id="v-count" class="small muted" aria-live="polite"></span>' +
      '<span class="v-pager"><button type="button" id="v-prev">‹ Previous</button>' +
      '<button type="button" id="v-next">Next ›</button>' +
      '<button type="button" id="v-dl">Download these rows</button><button type="button" id="v-reset">Reset</button></span></div>' +
      '<div class="table-scroll data"><table><thead></thead><tbody></tbody></table></div>';

    var thead = box.querySelector("thead"), tbody = box.querySelector("tbody");
    var result = rows;

    function apply() {
      var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
      if (terms.length && !lower) lower = rows.map(function (r) { return r.join("\u0001").toLowerCase(); });
      var fk = Object.keys(state.filters);
      result = [];
      for (var r = 0; r < rows.length; r++) {
        var row = rows[r], ok = true;
        for (var f = 0; f < fk.length && ok; f++) ok = (row[fk[f]] || "") === state.filters[fk[f]];
        for (var t = 0; t < terms.length && ok; t++) ok = lower[r].indexOf(terms[t]) !== -1;
        if (ok) result.push(row);
      }
      if (state.sort !== null) {
        var c = cols[state.sort], d = state.dir;
        result = result.slice().sort(function (a, b) {
          var x = a[c.i] || "", y = b[c.i] || "";
          if (c.numeric && isNum(x) && isNum(y)) return (num(x) - num(y)) * d;
          return x.localeCompare(y, undefined, { numeric: true }) * d;
        });
      }
      state.page = 0;
      render();
    }

    function cell(c, v) {
      if (c.name === "view" && v) return '<a href="' + esc(v) + '">Read</a>';
      if (/^https?:\/\//.test(v)) {
        // data.cso.ie/table/X links now redirect to the CSO home page; link to the table's data instead.
        var cso = v.match(/^https?:\/\/data\.cso\.ie\/table\/(\w+)\/?$/i);
        if (cso) v = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/" + cso[1].toUpperCase() + "/CSV/1.0/en";
        var label = v.replace(/^https?:\/\/(www\.)?/, "");
        return '<a href="' + esc(v) + '" title="' + esc(v) + '">' + esc(label.length > 40 ? label.slice(0, 40) + "…" : label) + '</a>';
      }
      return esc(v.length > 200 ? v.slice(0, 200) + "…" : v);
    }

    function render() {
      thead.innerHTML = "<tr>" + shown.map(function (c) {
        var mark = state.sort === c.i ? (state.dir > 0 ? " ▲" : " ▼") : "";
        return '<th' + (c.numeric ? ' class="num"' : "") + '><button type="button" data-sort="' + c.i + '" title="Sort">' + esc(c.name) + mark + "</button></th>";
      }).join("") + "</tr>";
      var start = state.page * PAGE, slice = result.slice(start, start + PAGE);
      tbody.innerHTML = slice.map(function (row) {
        return "<tr>" + shown.map(function (c) {
          return "<td" + (c.numeric ? ' class="num"' : c.long ? ' class="long"' : "") + ">" + cell(c, row[c.i] == null ? "" : row[c.i]) + "</td>";
        }).join("") + "</tr>";
      }).join("") || '<tr><td colspan="' + shown.length + '" class="muted">No rows match.</td></tr>';
      var total = rows.length.toLocaleString(), m = result.length.toLocaleString();
      document.getElementById("v-count").textContent = result.length
        ? "Rows " + (start + 1).toLocaleString() + "–" + (start + slice.length).toLocaleString() + " of " + m +
          (result.length < rows.length ? " (filtered from " + total + ")" : "")
        : "0 of " + total + " rows";
      document.getElementById("v-prev").disabled = state.page === 0;
      document.getElementById("v-next").disabled = start + PAGE >= result.length;
    }

    var timer;
    document.getElementById("v-q").addEventListener("input", function (e) {
      clearTimeout(timer);
      timer = setTimeout(function () { state.q = e.target.value; apply(); }, rows.length > 50000 ? 300 : 120);
    });
    box.querySelectorAll("select[data-col]").forEach(function (s) {
      s.addEventListener("change", function () {
        var i = s.getAttribute("data-col");
        if (s.value === "" && s.selectedIndex === 0) delete state.filters[i]; else state.filters[i] = s.value;
        apply();
      });
    });
    thead.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-sort]");
      if (!b) return;
      var i = +b.getAttribute("data-sort");
      state.dir = state.sort === i ? -state.dir : 1;
      state.sort = i;
      apply();
    });
    document.getElementById("v-prev").addEventListener("click", function () { state.page--; render(); });
    document.getElementById("v-next").addEventListener("click", function () { state.page++; render(); });
    document.getElementById("v-reset").addEventListener("click", function () {
      state = { q: "", filters: {}, sort: null, dir: 1, page: 0 };
      document.getElementById("v-q").value = "";
      box.querySelectorAll("select[data-col]").forEach(function (s) { s.selectedIndex = 0; });
      apply();
    });
    document.getElementById("v-dl").addEventListener("click", function () {
      var blob = new Blob([Papa.unparse([header].concat(result))], { type: "text/csv" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = (box.getAttribute("data-src").split("/").pop().replace(/\.\w+$/, "") || "data") + "-filtered.csv";
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    });
    render();
  }
})();
