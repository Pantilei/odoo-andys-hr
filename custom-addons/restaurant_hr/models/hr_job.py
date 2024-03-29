from odoo import _, api, fields, models
from odoo.osv import expression


class HrJob(models.Model):
    _inherit = "hr.job"

    name = fields.Char(
        string='Job Position',
        required=True,
        index=True
    )

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.env.user.department_id
    )

    branch_id = fields.Many2one(
        comodel_name="restaurant_hr.hr_branch",
        string="Branch"
    )

    hr_job_group_id = fields.Many2one(
        comodel_name="restaurant_hr.hr_job_group",
        string="Available Job Names"
    )

    current_application_count = fields.Integer(
        compute='_compute_no_emp_application_count', string="Current Applicants",
        help="Number of applications that are currently in the flow. Those who are not dismissed or not created employee from.")

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if self.env.context.get("show_job_name_only"):
                name = name
            elif department_id := record.department_id:
                name = f'{name} [{department_id.name}]'
            res.append((record.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = ['|', ("name", operator, name),
                  ("department_id.name", operator, name)]

        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.onchange("hr_job_group_id")
    def set_name(self):
        self.name = self.hr_job_group_id.name

    @api.depends('application_count', 'new_application_count')
    def _compute_no_emp_application_count(self):
        for job in self:
            job.current_application_count = self.env['hr.applicant'].search_count([
                ("emp_id", "=", False),
                ("job_id", "=", job.id),
            ])
