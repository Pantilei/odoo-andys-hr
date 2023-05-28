# -*- coding: utf-8 -*-

import json

from odoo import _, api, models


class EmployeeCardReport(models.AbstractModel):
    _name = 'report.restaurant_hr.employee_card_report'
    _description = 'Employee Card Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        lang = self.env.user.lang
        docs = self.env["hr.employee"].with_context(lang=lang).browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': self.env['hr.employee'],
            'data': data,
            'lang': lang,
            "employee_card_dicts": [json.loads(doc.employee_card_json) for doc in docs],
            'docs': docs
        }
