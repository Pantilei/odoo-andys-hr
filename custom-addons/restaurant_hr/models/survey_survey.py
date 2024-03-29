from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    title = fields.Char('Survey Title', required=True, translate=False) 
    description = fields.Html(
        "Description", translate=False, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="The description will be displayed on the home page of the survey. You can use this to give the purpose and guidelines to your candidates before they start it.")
    
    description_done = fields.Html(
        "End Message", translate=False,
        help="This message will be displayed when survey is completed")
    
    wage_rate_waiter_ids = fields.One2many(
        comodel_name="survey.survey_wage_rate",
        inverse_name="survey_id",
        string="Wage Rate for Waiter"
    )

    wage_rate_cook_small_department_ids = fields.One2many(
        comodel_name="survey.survey_wage_rate",
        inverse_name="survey_id",
        domain=[('department_size', '=', 'small')],
        context={'default_department_size': 'small'},
        string="Wage Rate for Cook within Small Department"
    )

    wage_rate_cook_medium_department_ids = fields.One2many(
        comodel_name="survey.survey_wage_rate",
        inverse_name="survey_id",
        domain=[('department_size', '=', 'medium')],
        context={'default_department_size': 'medium'},
        string="Wage Rate for Cook within Medium Department"
    )

    wage_rate_cook_large_department_ids = fields.One2many(
        comodel_name="survey.survey_wage_rate",
        inverse_name="survey_id",
        domain=[('department_size', '=', 'large')],
        context={'default_department_size': 'large'},
        string="Wage Rate for Cook within Large Department"
    )

    survey_group = fields.Selection(
        selection=[
            ("general", "General"),
            ("waiter", "Waiter"),
            ("cook", "Cook"),
        ],
        default="general",
        string="Survey Group",
        help="Survey group defines how the wage rate is calculated for the employee!"
    )

    users_with_access_ids = fields.Many2many(
        comodel_name="res.users",
        string="Allowed Users",
        help="Users who are able to edit/read the survey."
    )


class SurveyQuestion(models.Model):
    _inherit = "survey.question"
    title = fields.Char('Title', required=True, translate=False)
    description = fields.Html(
        'Description', sanitize=False, translate=False,
        help="Use this field to add additional explanations about your question or to illustrate it with pictures or a video"
    )
    comments_message = fields.Char('Comment Message', translate=False, default=lambda self: _("If other, please specify:"))
    validation_error_msg = fields.Char('Validation Error message', translate=False, default=lambda self: _("The answer you entered is not valid."))
    constr_error_msg = fields.Char('Error message', translate=False, default=lambda self: _("This question requires an answer."))


class SurveyQuestionAnswer(models.Model):
    _inherit = 'survey.question.answer'

    value = fields.Char('Suggested value', translate=False, required=True)  


class SurveySurveyBonuses(models.Model):
    _name = "survey.survey_wage_rate"
    _description = "Survey Wage Rate"

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

    wage_rate_min = fields.Float(
        string="Wage Rate Min",
        required=True
    )
    wage_rate_max = fields.Float(
        string="Wage Rate Max",
        required=True
    )

    department_size = fields.Selection(
        selection=[
            ("small", "Small"),
            ("medium", "Medium"),
            ("large", "Large"),
        ],
        string="Department Size",
        help="""
            If department is the restaurant, you can specify its size, the salaries of certain employees will 
            depend on it.
        """
    )
