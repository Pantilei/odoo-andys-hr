from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    bonuse_rate_ids = fields.One2many(
        comodel_name="survey.survey_bonuses",
        inverse_name="survey_id",
        string="Bonuses"
    )


class SurveySurveyBonuses(models.Model):
    _name = "survey.survey_bonuses"
    _description = "Survey Bonuses"

    @api.constrains("scoring_from")
    def scoring_range_constrains(self):
        for record in self:
            if record.scoring_from > record.scoring_to:
                raise UserError(
                    _("Scoring from must be lesser than scoring to!"))

    survey_id = fields.Many2one(
        comodel_name="survey.survey",
        required=True
    )

    scoring_from = fields.Float(
        string="Scoring from",
        required=True
    )

    scoring_to = fields.Float(
        string="Scoring to",
        required=True
    )

    interes_rate = fields.Float(
        string="Interest Rate",
        required=True
    )
