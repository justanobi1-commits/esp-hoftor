// ───────────────────────────────────────────────────────────────
//  hoftor_help.js — Bedien-Anleitung über dem Live-Log (web_server v3)
//  v1.0 | 2026-06-01 20:30:00
//
//  Eingebunden via  web_server: js_include: hoftor_help.js
//  → wird als /0.js ZUSÄTZLICH zum Frontend-Bundle (www.js) geladen
//    (beide <script> unabhängig in der ESPHome-index.html).
//
//  Zweck: fügt einen Anleitungs-Block als erstes Kind von #col_logs
//  (rechte Spalte, oberhalb des Live-Logs / „Debug") ein.
//
//  Warum JS statt CSS: #col_logs liegt im Shadow-DOM von <esp-app>.
//  Das globale css_include (/0.css) durchdringt den Shadow NICHT
//  (nur CSS-Custom-Properties / Farb-Variablen kommen durch) — am
//  laufenden Gerät verifiziert. Element-/content-Regeln greifen dort
//  nicht, daher die DOM-Injektion per Script.
//
//  type=module ⇒ wird garantiert als UTF-8 interpretiert (Umlaute ok)
//  und läuft deferred nach dem HTML-Parse.
// ───────────────────────────────────────────────────────────────
(function () {
  var CSS = 'color:#ffcc99;background:#15151f;border-left:4px solid #ff9900;' +
            'border-radius:4px;padding:12px 16px;margin:0 0 14px 0;' +
            'font-size:.82em;line-height:1.5';
  var HTML =
    '<div style="font-weight:bold;color:#ff9900;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;font-size:1.05em">Bedienung</div>' +
    '<p style="margin:0 0 7px"><b>Öffnen</b>: kurzer Impuls, beide Flügel auf. <b>Dauerauf</b>: hält offen bis Aus (schließt dann nach 1 s). <b>Auto-Schließ-Zeit</b>: Sek bis automatisch zu (0 = aus).</p>' +
    '<p style="margin:0 0 7px"><b>Schließen</b>: beide Flügel zu. <b>Auf-stopp-zu</b>: öffnen → stopp → schließen. Gesperrt bei aktivem Dauerauf.</p>' +
    '<p style="margin:0 0 7px"><b>Fußgänger</b>: nur ein Flügel. <b>Fußgänger-Dauerauf</b>: hält ihn offen. Öffnen bleibt möglich (Tor kehrt danach zurück).</p>' +
    '<p style="margin:0 0 7px">Dauerauf und Fußgänger-Dauerauf nie gleichzeitig. Taster am Tor öffnet nie selbst. LED blau = offen, rot = Dauerauf.</p>' +
    '<p style="margin:0"><b>Störung</b>: hängt das Tor zu lange, schließt der ESP automatisch (Esk1) → sonst meldet Esk2 an Home Assistant.</p>';

  function inject() {
    var app = document.querySelector('esp-app');
    if (!app || !app.shadowRoot) return false;
    var col = app.shadowRoot.querySelector('#col_logs');   // rechte Spalte (Log)
    if (!col) return false;                                 // nur wenn log: true
    if (app.shadowRoot.getElementById('hoftor-help')) return true;  // schon da
    var box = document.createElement('div');
    box.id = 'hoftor-help';
    box.style.cssText = CSS;
    box.innerHTML = HTML;
    col.insertBefore(box, col.firstChild);
    return true;
  }

  // sofort versuchen; falls App noch nicht gerendert → bis zu 60 s pollen
  if (!inject()) {
    var n = 0;
    var iv = setInterval(function () {
      if (inject() || ++n > 120) clearInterval(iv);
    }, 500);
  }

  // Re-Inject, falls esp-app sein Shadow-DOM neu rendert (z.B. Layout-Toggle).
  // Log-Updates triggern das NICHT (eigener Shadow-Tree in <esp-log>).
  // Retry bis App im DOM ist (läuft parallel zum inject-Polling, unabhängig davon).
  (function setupObserver() {
    var app = document.querySelector('esp-app');
    if (app && app.shadowRoot) {
      new MutationObserver(inject).observe(app.shadowRoot, { childList: true, subtree: true });
    } else {
      setTimeout(setupObserver, 500);
    }
  })();
})();
