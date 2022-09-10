from dataclasses import field
from odoo import api, models, fields, _


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

    hr_job_name_id = fields.Many2one(
        comodel_name="restaurant_hr.available_hr_job_names",
        string="Job Name"
    )

    @api.onchange("hr_job_name_id")
    def set_name(self):
        self.name = self.hr_job_name_id.name
