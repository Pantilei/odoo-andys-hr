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

        return request.render("restaurant_hr.employee_card", {
            "employee_id": employee_id.id,
            "employee_name": employee_id.name,
            "mobile_phone": employee_id.mobile_phone or '',
            "work_phone": employee_id.work_phone or '',
            "entry_date": employee_id.entry_date or '',
            "job_name": employee_id.job_id.name or '',
            "birth_date": "20-12-1993",
            "title": "THIS IS THE PAGE",
        })
