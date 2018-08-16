/**
 * Copyright (c) 2018 SPARKL Limited. All Rights Reserved.
 * Author <jacoby@sparkl.com> Jacoby Thwaites
 * Utility functions for SPARKL render.
 */

// Global state.
var state = {
  auto_refresh_rate: 0
};

/**
 * Attach open/close event handler to icons.
 */
var icons =
  document.getElementsByClassName(
    "icon open-close");
for (var i = 0; i < icons.length; i++) {
  var icon = icons[i];
  icon.onclick = function(event) {
    var results =
      document.evaluate(
        "ancestor::*[@action='open-close'][1]",
        event.target, null, null, null);
    var container =
      results.iterateNext();
    if (container) {
      var cls = container.getAttribute("class");
      if (cls == "opened") {
        container.setAttribute("class", "closed");
      }
      else {
        container.setAttribute("class", "opened");
      }
    }
  };
}

/**
 * Reload if the refresh query is present.
 */
var href = window.location.href;
var query = href.split("?")[1];
if (query) {
  var delay = Number(query) * 2000;
  if (delay) {
    setTimeout(
      function() {
        window.location.reload();
      }, delay);
  }
}
