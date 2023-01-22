# -*- coding: utf-8 -*-

import logging

import werkzeug

from odoo import _, http
from odoo.addons.survey.controllers.main import Survey
from odoo.http import request
from odoo.tools import format_date, format_datetime, is_html_empty

_logger = logging.getLogger(__name__)


class EmployeeAssesment(http.Controller):

    @http.route('/assessment/<string:short_access_token>', type='http', auth="public")
    def get_employee_card(self, short_access_token, **kw):
        user_input_id = request.env["survey.user_input"].sudo().search([
            ("short_access_token", "=", short_access_token)
        ])

        if not user_input_id:
            raise werkzeug.exceptions.NotFound()
        
        params = werkzeug.urls.url_encode({'answer_token': user_input_id.access_token})
        return request.redirect(f'{user_input_id.survey_id.get_start_url()}?{params}')


class SurveyInherit(Survey):
    @http.route('/survey/print/<string:survey_token>', type='http', auth='public', website=True, sitemap=False)
    def survey_print(self, survey_token, review=False, answer_token=None, **post):
        '''Display an survey in printable view; if <answer_token> is set, it will
        grab the answers of the user_input_id that has <answer_token>.'''
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False, check_partner=False)
        if access_data['validity_code'] is not True and (
                access_data['has_survey_access'] or
                access_data['validity_code'] not in ['token_required', 'survey_closed', 'survey_void']):
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

        if request.env.user.has_group("survey.group_survey_user"):
            return request.render('survey.survey_page_print', {
                'is_html_empty': is_html_empty,
                'review': review,
                'survey': survey_sudo,
                'answer': answer_sudo,
                'questions_to_display': answer_sudo._get_print_questions(),
                'scoring_display_correction': answer_sudo,
                'format_datetime': lambda dt: format_datetime(request.env, dt, dt_format=False),
                'format_date': lambda date: format_date(request.env, date),
            })
        return request.render('survey.survey_page_print', {
            'is_html_empty': is_html_empty,
            'review': review,
            'survey': survey_sudo,
            'answer': answer_sudo if survey_sudo.scoring_type != 'scoring_without_answers' else answer_sudo.browse(),
            'questions_to_display': answer_sudo._get_print_questions(),
            'scoring_display_correction': survey_sudo.scoring_type == 'scoring_with_answers' and answer_sudo,
            'format_datetime': lambda dt: format_datetime(request.env, dt, dt_format=False),
            'format_date': lambda date: format_date(request.env, date),
        })
