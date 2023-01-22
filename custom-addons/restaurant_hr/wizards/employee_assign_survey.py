import logging

import werkzeug

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.Logger(__name__)


class EmployeeAssignSurveyWizard(models.TransientModel):
    _name = "restaurant_hr.employee_assign_survey_wizard"
    _description = "Employee assign survey wizard"

    survey_id = fields.Many2one(
        comodel_name="survey.survey",
        required=True,
        domain=[("certification", "=", True)]
    )

    employee_ids = fields.Many2many(
        comodel_name="hr.employee", 
        string="Employees",
        default=lambda self: self.env.context.get("employee_ids")
    )

    def confirm(self):
        UserInput = self.env["survey.user_input"]
        for employee_id in self.employee_ids:
            response_id = UserInput.search([
                ("employee_id", "=", employee_id.id),
                ("survey_id", "=", self.survey_id.id),
                ("state", "=", "new"),
            ])
            if not response_id:
                response_id = self.survey_id._create_answer(
                    survey_id=self.survey_id.id,
                    partner_id=self.env.user.partner_id.id,
                    email=employee_id.work_email,
                    employee_id=employee_id.id
                )
            employee_id.response_ids |= response_id
            
        return {
            'name': _('Survey Links'),
            'type': 'ir.actions.act_window',
            'res_model': 'survey.user_input',
            'views': [(self.env.ref("restaurant_hr.survey_user_input_form").id, "tree")],
            'context': {},
            "domain": [
                ("employee_id", "in", self.employee_ids.ids),
                ("survey_id", "=", self.survey_id.id),
                ("state", "=", "new")
            ],
            'target': 'current'
        }

