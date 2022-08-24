import werkzeug

from odoo import models, fields, api, _


class SurveryUserInput(models.Model):
    _inherit = "survey.user_input"

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee"
    )

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
