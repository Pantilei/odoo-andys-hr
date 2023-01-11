from odoo import _, api, fields, models
from odoo.exceptions import UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]

class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    response_ids = fields.One2many(
        comodel_name="survey.user_input",
        inverse_name="applicant_id",
        string="Responces",
        groups="survey.group_survey_user"
    )

    source_id = fields.Many2one(
        comodel_name='utm.source', 
        string='Source',
        ondelete="restrict",
        help="This is the source of the link, e.g. Search Engine, another domain, or name of email list"
    )

    priority = fields.Selection(
        string="Priority",
    )

    branch_id = fields.Many2one(
        comodel_name="restaurant_hr.hr_branch",
        string="Branch"
    )

    birthday = fields.Date(string="Birthday")

    last_response_score = fields.Float(
        string="Last Score (%)",
        compute="_compute_last_responce_score",
        store=True
    )

    application_type = fields.Selection([
        ("linear", "Linear Personal"),
        ("administrative", "Administrative Personal"),
        ("factory", "Factory"),
    ], default="linear", string="Application Type", required=True)

    def write(self, vals):
        if "emp_id" in vals:
            hired_stage_id = self.env["hr.recruitment.stage"].search(
                [("hired_stage", "=", True)], limit=1)
            vals["stage_id"] = hired_stage_id.id
        return super(HrApplicant, self).write(vals)

    @api.depends("response_ids.scoring_percentage")
    def _compute_last_responce_score(self):
        for record in self:
            sorted_responses = record.response_ids\
                .filtered(lambda r: r.state == "done")\
                .sorted(key=lambda r: r.create_date)
            record.last_response_score = sorted_responses[0].scoring_percentage if sorted_responses else False

    def assess_applicant(self):
        return {
            'name': _('Select Survey'),
            'type': 'ir.actions.act_window',
            'res_model': 'restaurant_hr.applicant_survey_select_wizard',
            'views': [(False, "form")],
            'context': {
                'applicant_id': self.id,
            },
            'target': 'new'
        }

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])[
                    'contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(
                        _('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                applicant.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                employee_data = {
                    'default_name': applicant.partner_name or contact_name,
                    'default_job_id': applicant.job_id.id,
                    'default_job_title': applicant.job_id.name,
                    'default_address_home_id': address_id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                    and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.department_id and applicant.department_id.company_id
                    and applicant.department_id.company_id.email or False,
                    'default_work_phone': applicant.department_id.company_id.phone,
                    'default_applicant_id': applicant.ids,
                    'default_response_ids': [(6, 0, applicant.response_ids.ids)],
                    'default_employee_type': 'trainee',
                    'default_source_id': applicant.source_id.id,

                    'form_view_initial_mode': 'edit',
                }

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id(
            'restaurant_hr.employee_full_management_form_action')
        dict_act_window['context'] = employee_data
        return dict_act_window
