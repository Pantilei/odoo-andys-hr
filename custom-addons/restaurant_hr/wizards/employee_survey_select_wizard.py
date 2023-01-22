import werkzeug

from odoo import _, api, fields, models


class EmployeeSurveySelectWizard(models.TransientModel):
    _name = "restaurant_hr.employee_survey_select_wizard"
    _description = "Employee Survey Select Wizard"

    survey_id = fields.Many2one(
        comodel_name="survey.survey",
        string="Survey",
        required=True,
        domain=[("certification", "!=", True)]
    )

    manager_id = fields.Many2one(
        comodel_name="res.partner",
        string="Appraiser",
        default=lambda self: self.env.user.partner_id
    )

    def confirm(self):
        employee_id = self.env["hr.employee"].search([
            ("id", "=", self.env.context.get("employee_id"))
        ], limit=1)
        response_id = self.survey_id._create_answer(
            survey_id=self.survey_id.id,
            partner_id=self.manager_id.id,
            email=employee_id.work_email,
            employee_id=employee_id.id
        )
        employee_id.response_ids |= response_id

        url = '%s?%s' % (self.survey_id.get_start_url(), werkzeug.urls.url_encode(
            {'answer_token': response_id and response_id.access_token or None}))
        return {
            'type': 'ir.actions.act_url',
            'name': _("Start Survey"),
            'target': 'new',
            'url': url,
        }
