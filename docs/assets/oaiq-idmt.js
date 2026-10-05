/* IDMT — OpenAI Ads Measurement Pixel integration. */
(function (w, d, s, u) {
  if (w.oaiq) return;
  var q = function () { q.q.push(arguments); };
  q.q = [];
  w.oaiq = q;
  var js = d.createElement(s);
  js.async = true;
  js.src = u;
  var f = d.getElementsByTagName(s)[0];
  f.parentNode.insertBefore(js, f);
})(window, document, "script", "https://bzrcdn.openai.com/sdk/oaiq.min.js");

oaiq("init", {
  pixelId: "TZrpbXCpUoNe2fLiVrFMs9",
  debug: Boolean(window.IDMT_OAIQ_DEBUG)
});

(function () {
  function eventId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
    return "idmt-" + Date.now() + "-" + Math.random().toString(36).slice(2);
  }

  function measure(name, data, options) {
    if (!window.oaiq) return null;
    var id = (options && options.event_id) || eventId();
    var opts = Object.assign({}, options || {}, { event_id: id });
    window.oaiq("measure", name, data || { type: "custom" }, opts);
    return id;
  }

  window.IDMTAds = {
    measure: measure,
    leadCreated: function (extra) {
      return measure("lead_created", Object.assign({ type: "customer_action" }, extra || {}));
    },
    appointmentScheduled: function (extra, existingEventId) {
      return measure(
        "appointment_scheduled",
        Object.assign({ type: "customer_action" }, extra || {}),
        existingEventId ? { event_id: existingEventId } : undefined
      );
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    measure("page_viewed", {
      type: "contents",
      contents: [{
        id: document.title || window.location.pathname,
        name: document.title || window.location.pathname,
        quantity: 1
      }]
    });

    document.querySelectorAll("[data-oaiq-event]").forEach(function (el) {
      el.addEventListener("click", function () {
        var name = el.getAttribute("data-oaiq-event");
        if (!name) return;
        var data = { type: "customer_action" };
        var label = el.getAttribute("data-oaiq-label");
        if (label) data.label = label;
        measure(name, data);
      });
    });
  }
})();
