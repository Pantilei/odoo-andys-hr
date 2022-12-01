# -*- coding: utf-8 -*-

import logging
import werkzeug


from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class EmployeeCard(http.Controller):

    @http.route('/hr/employee-card/<int:employee_id>', type='http', auth="user")
    def get_employee_card(self, employee_id, **kw):
        """ Reviews """
        employee_id = request.env["hr.employee"].search(
            [("id", "=", employee_id)])
        if not employee_id:
            return werkzeug.exceptions.NotFound()

        resume_section_ids = employee_id.resume_line_ids.mapped(
            "line_type_id")
        return request.render("restaurant_hr.employee_card", {
            "employee_id": employee_id.id,
            "employee_name": employee_id.name,
            "mobile_phone": employee_id.mobile_phone or '',
            "work_phone": employee_id.work_phone or '',
            "entry_date": employee_id.entry_date or '',
            "job_name": employee_id.job_id.name or '',
            "birthday": employee_id.birthday or '',
            "resume_section_ids": [{
                "section_id": resume_section_id.id,
                "section_name": resume_section_id.name,
                "section_data": [{
                    "resume_line_id": resume_line_id.id,
                    "name": resume_line_id.name,
                    "description": resume_line_id.description,
                    "date_start": resume_line_id.date_start,
                    "date_end": resume_line_id.date_end,
                } for resume_line_id in employee_id.resume_line_ids.filtered(lambda r: r.line_type_id.id == resume_section_id.id)]
            } for resume_section_id in resume_section_ids],
            "remarks": [{
                "remark_id": remark.id,
                "remark_description": remark.description,
                "remark_date": remark.assigment_date,
            } for remark in employee_id.employee_remark_ids],
            "achievements": [{
                "achievement_id": achievement.id,
                "achievement_description": achievement.description,
                "achievement_date": achievement.assigment_date,
            } for achievement in employee_id.employee_achievement_ids],
            "responses": [{
                "response_id": response.id,
                "name": response.survey_id.title,
                "scoring_percentage": response.scoring_percentage,
                "create_date": response.create_date.strftime("%Y-%m-%d"),
            } for response in employee_id.response_ids],
            "title": "THIS IS THE PAGE",
        })
