odoo.define("review.form", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var time = require("web.time");
  var core = require("web.core");
  var Dialog = require("web.Dialog");
  var dom = require("web.dom");
  var utils = require("web.utils");

  var _t = core._t;

  $.validator.addMethod(
    "customphone",
    function (value, element) {
      return this.optional(element) || /^\d{3}-\d{3}-\d{4}$/.test(value);
    },
    "Please enter a valid phone number"
  );

  publicWidget.registry.ReviewsWidget = publicWidget.Widget.extend({
    selector: ".o_reviews_form",
    events: {
      "click .o_submit_button": "_onSubmit",
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
        self.$form = self.$("#review_form");
        const queryParams = self._getQueryParams();
        const lang = queryParams.lang;

        self.$form.validate({
          // Specify validation rules
          rules: {
            name: "required",
            phone: "required",
            email_from: {
              required: false,
              email: true,
            },
            description: {
              required: true,
              minlength: 5,
            },
          },
          // Specify validation error messages
          messages: self._validationMessagesTranslations(lang),
        });
      });
    },

    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------

    _validationMessagesTranslations: function (lang) {
      let currentLang = ["en", "ro", "ru"].includes(lang) ? lang : "ro";
      const messages = {
        en: {
          name: "Enter your name!",
          phone: "Enter your phone!",
          email_from: "Enter valid email!",
          description: {
            required: "Enter your feedback!",
            minlength: "Your feedback is too short!",
          },
        },
        ru: {
          name: "Введите ваше имя!",
          phone: "Введите ваш телефон!",
          email_from: "Введите правильный email!",
          description: {
            required: "Введите ваш отзыв!",
            minlength: "Ваш отзыв очень короткий!",
          },
        },
        ro: {
          name: "Introduceți numele dvs!",
          phone: "Introduceți telefonul dvs",
          email_from: "Introduceți un e-mail valid!",
          description: {
            required: "Introduceți feedback-ul dvs!",
            minlength: "Feedback-ul dvs. este prea scurt!",
          },
        },
      };
      return messages[currentLang];
    },

    _getQueryParams: function () {
      const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
      });
      return params;
    },

    // Handlers
    // -------------------------------------------------------------------------

    _onSubmit: function (event) {
      event.preventDefault();
      const queryParams = this._getQueryParams();
      const lang = queryParams.lang;
      if (this.$form.valid()) {
        var formData = new FormData(this.$form[0]);
        let dataToSend = {};
        formData.forEach(function (value, key) {
          dataToSend[key] = value;
        });

        return this._rpc({
          route: window.location.pathname + "/handle",
          params: dataToSend,
        }).then((r) => {
          if (r.success) {
            window.location.href =
              window.location.pathname + `/thank-you?lang=${lang}`;
          } else {
            console.log(r.message);
          }
        });
      }
    },
  });

  return publicWidget.registry.ReviewsWidget;
});
