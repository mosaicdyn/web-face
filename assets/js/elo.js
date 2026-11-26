/* FACEIT Elo calculator. Same maths as elo_estimate() in _build/pages.py. */
(function () {
  var form = document.getElementById("elo-calc");
  if (!form) return;
  // FACEIT CS2 levels: [level, minimum Elo]
  var LEVELS = [[1, 100], [2, 501], [3, 751], [4, 901], [5, 1051], [6, 1201], [7, 1351], [8, 1531], [9, 1751], [10, 2001]];
  var fmt = function (n) { return Math.round(n).toLocaleString("en-US"); };
  var out = function (key, value) { var el = form.querySelector('[data-out="' + key + '"]'); if (el) el.textContent = value; };
  var num = function (name, fallback, lo, hi) {
    var v = parseFloat(form.elements[name].value);
    if (!isFinite(v)) v = fallback;
    return Math.min(Math.max(v, lo), hi);
  };

  function levelOf(elo) {
    var lvl = 1;
    LEVELS.forEach(function (l) { if (elo >= l[1]) lvl = l[0]; });
    return lvl;
  }

  function update() {
    var elo = num("elo", 1300, 0, 10000);
    var target = num("target", 2001, 0, 10000);
    var wr = num("wr", 55, 1, 99);
    var perDay = num("perday", 3, 1, 50);
    var gain = num("gain", 25, 1, 100);
    var loss = num("loss", 25, 1, 100);

    var lvl = levelOf(elo);
    var next = LEVELS[lvl] ? LEVELS[lvl][1] - elo : 0;
    var diff = Math.max(target - elo, 0);
    var net = wr / 100 * gain - (1 - wr / 100) * loss;

    out("level", lvl);
    out("next", lvl === 10 ? "—" : fmt(next));
    out("diff", fmt(diff));
    out("netwins", diff ? fmt(Math.ceil(diff / gain)) : "0");

    if (diff === 0) {
      out("matches", "0");
      out("note", "You are already there.");
    } else if (Math.abs(net) < 1e-9) {
      out("matches", "—");
      out("note", "At " + wr + "% your wins and losses cancel out, so you stay where you are. Raise your win rate first.");
    } else if (net < 0) {
      out("matches", "—");
      out("note", "At " + wr + "% you lose Elo on average, so you won’t climb. Raise your win rate above 50% first.");
    } else {
      var matches = Math.ceil(diff / net);
      var days = Math.ceil(matches / perDay);
      out("matches", fmt(matches));
      out("note", "At " + wr + "% you gain about " + net.toFixed(1) + " Elo per match. At " + perDay + " matches a day that is about " + fmt(days) + " days.");
    }
  }

  form.addEventListener("input", update);
  form.addEventListener("change", update);
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  update();
})();
