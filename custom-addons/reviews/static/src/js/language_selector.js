odoo.define("language_selector", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var time = require("web.time");
  var core = require("web.core");
  var Dialog = require("web.Dialog");
  var dom = require("web.dom");
  var utils = require("web.utils");

  var _t = core._t;

  publicWidget.registry.LanguageSelector = publicWidget.Widget.extend({
    selector: ".language-selector",
    events: {
      change: "_onChange",
    },
    custom_events: {},

    //--------------------------------------------------------------------------
    // Widget
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    start: function () {
      var self = this;
      return this._super.apply(this, arguments).then(function () {
        const queryParams = self._getQueryParams();
        const lang = queryParams.lang;
        if (["en", "ro", "ru"].includes(lang)) {
          self.$el.val(lang);
        } else {
          self.$el.val("ro");
        }
      });
    },

    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------
    _getQueryParams: function () {
      const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
      });
      return params;
    },

    // Handlers
    // -------------------------------------------------------------------------

    _onChange: function (event) {
      event.preventDefault();
      console.log(event.target.value);
      window.location.href = `${window.location.pathname}?lang=${event.target.value}`;
    },
  });

  return publicWidget.registry.LanguageSelector;
});
