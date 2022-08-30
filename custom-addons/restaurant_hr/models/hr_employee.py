from odoo import api, models, fields, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.env.user.department_id
    )

    response_ids = fields.One2many(
        comodel_name="survey.user_input",
        inverse_name="employee_id",
        string="Responces",
        groups="survey.group_survey_user"
    )

    resume_pdf = fields.Binary(
        string="Resume PDF",
        groups="hr.group_hr_user",
        tracking=True
    )

    coach_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Coaches',
        # compute='_compute_coaches',
        relation="employee_coaches",
        column1="employee",
        column2="coach",
        store=True,
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" will have the opportunity to edit the information of his students.')

    # @api.depends('parent_id')
    # def _compute_coaches(self):
    #     for employee in self:
    #         manager = employee.parent_id
    #         if manager:
    #             employee.coach_ids |= manager
    #         else:
    #             employee.coach_ids = employee.coach_ids

    def assess_employee(self):
        return {
            'name': _('Select Survey'),
            'type': 'ir.actions.act_window',
            'res_model': 'restaurant_hr.employee_survey_select_wizard',
            'views': [(False, "form")],
            'context': {
                'employee_id': self.id,
            },
            'target': 'new'
        }
