import random
import string

import werkzeug

from odoo import _, api, fields, models


def short_uuid():
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=11))

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

    applicant_name = fields.Char(
        string="Applicant",
        related="applicant_id.partner_name"
    )

    short_access_token = fields.Text(
        string="Short Access Token",
        compute="_compute_short_token",
        store=True,
        index=True
    )

    short_access_url = fields.Text(
        string="Short Access URL",
        compute="_compute_short_url"
    )

    is_certificate = fields.Boolean(
        related="survey_id.certification"
    )

    @api.model
    def create(self, vals):
        user_input_line = super().create(vals)
        if user_input_line.employee_id:
            content = _('New assessment "%s" has been assigned on employee', user_input_line.survey_id.title)
            body = f'<p>{content}</p>'
            user_input_line.employee_id.message_post(body=body)
        return user_input_line
    
    @api.model
    def unlink(self):
        if self.employee_id:
            content = _(
                'Assessment "%s" with %s(%s%%) scoring has been deleted from employee', 
                self.survey_id.title,
                self.scoring_total,
                self.scoring_percentage
            )
            body = f'<p>{content}</p>'
            self.employee_id.message_post(body=body)
        return super().unlink()

    @api.depends("access_token")
    def _compute_short_token(self):
        for record in self:
            record.short_access_token = short_uuid()
    
    @api.depends("access_token")
    def _compute_short_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.short_access_url = f"{base_url}/assessment/{record.short_access_token}"

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
