odoo.define('review.form', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');
var core = require('web.core');
var Dialog = require('web.Dialog');
var dom = require('web.dom');
var utils = require('web.utils');

var _t = core._t;


$.validator.addMethod('customphone', function (value, element) {
    return this.optional(element) || /^\d{3}-\d{3}-\d{4}$/.test(value);
},
    "Please enter a valid phone number"
);


publicWidget.registry.ReviewsWidget = publicWidget.Widget.extend({
    selector: '.o_reviews_form',
    events: {
        'click .o_submit_button': '_onSubmit',
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
            self.$form = self.$('#review_form');
            self.$form.validate({
                // Specify validation rules
                rules: {
                    name: "required",
                    email_from: {
                        required: false,
                        email: true,
                    },
                    description: {
                        required: true,
                        minlength: 10,
                    }
                },
                // Specify validation error messages
                messages: {
                    name: "Введите ваше имя!",
                    email_from: "Введите правильный email!",
                    description: {
                        required: "Введите ваш отзыв!",
                        minlength: "Ваш отзыв очень короткий!",
                    },
                }
            });
        });
    },

    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------

    // Handlers
    // -------------------------------------------------------------------------

    _onSubmit: function (event) {
        event.preventDefault();
        if (this.$form.valid()) {
            var route = "/reviews/submit";
            var formData = new FormData(this.$form[0]);
            let dataToSend = {}
            formData.forEach(function (value, key) {
                dataToSend[key] = value;
            });

            console.log("dataToSend", dataToSend);
            return this._rpc({
                route: window.location.pathname + "/handle",
                params: dataToSend,
            }).then(r => {
                if (r.success) {
                    window.location.href = "/reviews/thank-you"
                } else {
                    console.log(r.message);
                }
            })
        }

    },
});

return publicWidget.registry.ReviewsWidget;

});
