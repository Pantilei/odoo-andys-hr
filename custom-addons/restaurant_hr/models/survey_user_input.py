import werkzeug

from odoo import models, fields, api, _


class SurveryUserInput(models.Model):
    _inherit = "survey.user_input"

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee"
    )

    applicant_id = fields.Many2one(
        comodel_name="hr.applicant",
        string="Applicant"
    )

    bonuse_percentage = fields.Float(
        string="Bonuse Percentage",
        compute="_compute_bonuse_percentage"
    )

    @api.depends("scoring_percentage", "survey_id")
    def _compute_bonuse_percentage(self):
        for record in self:
            bonuse_percentage = 0
            for line in record.survey_id.bonuse_rate_ids:
                if line.scoring_from <= record.scoring_percentage/100 <= line.scoring_to:
                    bonuse_percentage = line.interes_rate
            record.bonuse_percentage = bonuse_percentage

    def proceed_survey(self):
        url = '%s?%s' % (self.survey_id.get_start_url(), werkzeug.urls.url_encode(
            {'answer_token': self.access_token or None}))
        return {
            'type': 'ir.actions.act_url',
            'name': _("Proceed Survey"),
            'target': 'new',
            'url': url,
        }

    def see_results(self):
        return {
            'type': 'ir.actions.act_url',
            'name': _("View Answers"),
            'target': 'new',
            'url': '/survey/print/%s?answer_token=%s' % (self.survey_id.access_token, self.access_token)
        }
