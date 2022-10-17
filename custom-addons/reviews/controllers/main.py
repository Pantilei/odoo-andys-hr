# -*- coding: utf-8 -*-

import json
import logging
import werkzeug
import base64

from datetime import datetime, timedelta, timezone

from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class Reviews(http.Controller):

    @http.route('/reviews', type='http', auth="public")
    def reviews_restaurnat_not_found(self, **kw):
        form_id = request.env["reviews.collection"].sudo().search([], limit=1)
        return request.render("reviews.reviews_restaurnat_not_found", {
            "title": "Ресторан не найден!",
            "company_support_phone": form_id.phone or "+1 (650) 555-0111",
            "company_support_email": form_id.email or "info@yourcompany.example.com",
            "reviews_collection_id": form_id.id,
        })

    @http.route('/reviews/<string:department_token>', type='http', auth="public")
    def reviews(self, department_token, **kw):
        """ Reviews """
        department_id = request.env["hr.department"].sudo().search([
            ("uid", "=", department_token)
        ], limit=1)
        if not department_id:
            return werkzeug.exceptions.NotFound()

        return request.render("reviews.reviews_page_fill", {
            "title": department_id.review_collection_id.name,
            "company_support_phone": department_id.review_collection_id.phone or "+1 (650) 555-0111",
            "company_support_email": department_id.review_collection_id.email or "info@yourcompany.example.com",
            "reviews_collection_id": department_id.review_collection_id.id,
        })

    @http.route('/reviews/<string:department_token>/thank-you', type='http', auth="public")
    def reviews_thank_you(self, department_token, **kw):
        """ Reviews Thank You"""
        department_id = request.env["hr.department"].sudo().search([
            ("uid", "=", department_token)
        ], limit=1)
        if not department_id:
            return werkzeug.exceptions.NotFound()
        return request.render("reviews.reviews_thankyou_page", {
            "title": department_id.review_collection_id.name,
            "company_support_phone": department_id.review_collection_id.phone or "+1 (650) 555-0111",
            "company_support_email": department_id.review_collection_id.email or "info@yourcompany.example.com",
            "reviews_collection_id": department_id.review_collection_id.id,
        })

    @http.route('/reviews/<string:department_token>/handle', type='json', auth="public",  website=True)
    def reviews_handle(self, department_token, **kw):
        """ Reviews Handle"""
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

    @http.route('/reviews/bg-img/<int:form_id>', type='http', auth="public")
    def reviews_bg_image(self, form_id, **kw):
        form_id = request.env["reviews.collection"].sudo().search([
            ("id", "=", form_id)
        ], limit=1)
        if not form_id:
            return werkzeug.exceptions.NotFound()
        return request.env['ir.http'].sudo()._content_image(model='reviews.collection', res_id=form_id, field='bg_img')
