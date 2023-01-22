import werkzeug

from odoo import _, api, fields, models


class ApplicantSurveySelectWizard(models.TransientModel):
    _name = "restaurant_hr.applicant_survey_select_wizard"
    _description = "Applicant Survey Select Wizard"

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
        applicant_id = self.env["hr.applicant"].search([
            ("id", "=", self.env.context.get("applicant_id"))
        ], limit=1)
        response_id = self.survey_id._create_answer(
            survey_id=self.survey_id.id,
            partner_id=self.manager_id.id,
            email=applicant_id.email_from,
            applicant_id=applicant_id.id
        )

        applicant_id.response_ids |= response_id

        url = '%s?%s' % (self.survey_id.get_start_url(), werkzeug.urls.url_encode(
            {'answer_token': response_id and response_id.access_token or None}))
        return {
            'type': 'ir.actions.act_url',
            'name': _("Start Survey"),
            'target': 'new',
            'url': url,
        }
