# -*- coding: utf-8 -*-

import json
import logging
import werkzeug

from datetime import datetime, timedelta, timezone

from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class Reviews(http.Controller):

    @http.route('/reviews/<string:department_token>', type='http', auth="public")
    def reviews(self, department_token, **kw):
        """ Reviews """
        department_id = request.env["hr.department"].sudo().search([
            ("uid", "=", department_token)
        ], limit=1)
        if not department_id:
            return werkzeug.exceptions.NotFound()
        return request.render("reviews.reviews_page_fill", {
            "title": "Отзывы Andys",
            "company_address": " 3575 Fake Buena Vista Avenue",
            "company_support_phone": "+1 (650) 555-0111",
            "company_support_email": "info@yourcompany.example.com",
        })

    @http.route('/reviews/<string:department_token>/thank-you', type='http', auth="public")
    def reviews_thank_you(self, department_token, **kw):
        """ Reviews """
        return request.render("reviews.reviews_thankyou_page", {
            "title": "Отзывы Andys",
            "company_address": " 3575 Fake Buena Vista Avenue",
            "company_support_phone": "+1 (650) 555-0111",
            "company_support_email": "info@yourcompany.example.com",
        })

    @http.route('/reviews/<string:department_token>/handle', type='json', auth="public",  website=True)
    def reviews_handle(self, department_token, **kw):
        """ Reviews """
        print("\n\n kw", kw)
        print("\n\n restaurant_token", department_token)
        if not kw.get("name", None) or not kw.get("description", None):
            return {
                "success": False,
                "message": "Name and review must be present!"
            }
        department_id = request.env["hr.department"].sudo().search([
            ("uid", "=", department_token)
        ], limit=1)
        if not department_id:
            return {
                "success": False,
                "message": "Department not found!"
            }
        request.env['reviews'].sudo().create({
            "name": kw.get("name"),
            "phone": kw.get("phone", False),
            "email": kw.get("email_from", False),
            "responsible_name": kw.get("name_of_responsible", False),
            "description": kw.get("description"),
            "department_id": department_id.id
        })
        return {
            "success": True,
            "message": ""
        }
