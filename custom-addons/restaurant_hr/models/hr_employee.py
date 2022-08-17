from odoo import api, models, fields, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.env.user.department_id
    )

    resume_pdf = fields.Binary(
        string="Resume PDF",
        groups="hr.group_hr_user",
        tracking=True
    )
