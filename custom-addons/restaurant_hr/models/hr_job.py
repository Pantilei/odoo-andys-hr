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
        string="Job Name"
    )

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
