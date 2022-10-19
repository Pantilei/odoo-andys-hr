# -*- coding: utf-8 -*-

import json
import logging
import werkzeug
import base64

from datetime import datetime, timedelta, timezone

from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


def _get_translations(lang):
    translations = {
        "en": {
            "Leave your feedback!": "Leave your feedback!",
            "Restaurant not found!": "Ресторан не найден!",
            "Your Name": "Your Name",
            "Tel": "Tel",
            "Email": "Email",
            "Responsible Name": "Responsible Name",
            "Your Feedback": "Your Feedback",
            "Send": "Send",
            "Thank you for your reviews!": "Thank you for your reviews!",
            "Contacts": "Contacts",
        },

        "ru": {
            "Leave your feedback!": "Оставьте ваш отзыв!",
            "Restaurant not found!": "Ресторан не найден!",
            "Your Name": "Ваше Имя",
            "Tel": "Тел",
            "Email": "Емайл",
            "Responsible Name": "Имя Ответственного",
            "Your Feedback": "Ваш отзыв",
            "Send": "Отправить",
            "Thank you for your reviews!": "Спасибо за Ваш отзыв и за то, что помогаете нам стать лучше!",
            "Contacts": "Контакты",
        },

        "ro": {
            "Leave your feedback!": "Lăsați-vă feedback!",
            "Restaurant not found!": "Restaurantul nu a fost găsit!",
            "Your Name": "Numele Dvs",
            "Tel": "Tel",
            "Email": "E-mail",
            "Responsible Name": "Numele responsabilului",
            "Your Feedback": "Feedback",
            "Send": "Trimite",
            "Thank you for your reviews!": "Vă mulțumim pentru recenzie și pentru că ne ajutați să devenim mai buni!",
            "Contacts": "Contacte",
        }
    }
    return translations.get(lang, "ro")


class Reviews(http.Controller):

    @http.route('/reviews', type='http', auth="public")
    def reviews_restaurnat_not_found(self, **kw):
        form_id = request.env["reviews.collection"].sudo().search([], limit=1)
        lang = kw.get("lang")
        lang = lang if (lang and lang in ["ru", "en", "ro"]) else 'ro'
        translate = _get_translations(lang)
        return request.render("reviews.reviews_restaurnat_not_found", {
            "title": translate("Restaurant not found!"),
            "company_support_phone": form_id.phone or "+1 (650) 555-0111",
            "company_support_email": form_id.email or "info@yourcompany.example.com",
            "translate": translate,
            "bg_image": f"{self._get_bg_image_base_url()}/{form_id.id}"
        })

    @http.route('/reviews/<string:department_token>', type='http', auth="public")
    def reviews(self, department_token, **kw):
        """ Reviews """
        print("\n\n kw", kw)
        lang = kw.get("lang")
        lang = lang if (lang and lang in ["ru", "en", "ro"]) else 'ro'
        department_id = request.env["hr.department"].sudo().search([
            ("uid", "=", department_token)
        ], limit=1)
        if not department_id or not department_id.review_collection_id:
            return werkzeug.exceptions.NotFound()

        return request.render("reviews.reviews_page_fill", {
            "title": department_id.review_collection_id.name,
            "company_support_phone": department_id.review_collection_id.phone or "+1 (650) 555-0111",
            "company_support_email": department_id.review_collection_id.email or "info@yourcompany.example.com",
            "translate": _get_translations(lang),
            "bg_image": f"{self._get_bg_image_base_url()}/{department_id.review_collection_id.id}"
        })

    @http.route('/reviews/<string:department_token>/thank-you', type='http', auth="public")
    def reviews_thank_you(self, department_token, **kw):
        """ Reviews Thank You"""
        department_id = request.env["hr.department"].sudo().search([
            ("uid", "=", department_token)
        ], limit=1)
        if not department_id or not department_id.review_collection_id:
            return werkzeug.exceptions.NotFound()

        lang = kw.get("lang")
        lang = lang if (lang and lang in ["ru", "en", "ro"]) else 'ro'
        return request.render("reviews.reviews_thankyou_page", {
            "title": department_id.review_collection_id.name,
            "company_support_phone": department_id.review_collection_id.phone or "+1 (650) 555-0111",
            "company_support_email": department_id.review_collection_id.email or "info@yourcompany.example.com",
            "translate": _get_translations(lang),
            "bg_image": f"{self._get_bg_image_base_url()}/{department_id.review_collection_id.id}"
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

    def _get_bg_image_base_url(self):
        return request.env["ir.config_parameter"].sudo().get_param("reviews.bg_image.url")
