<script><![CDATA[
/**
 * Copyright 2018 SPARKL Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
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
]]></script>
