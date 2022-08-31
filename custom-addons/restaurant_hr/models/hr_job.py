from odoo import api, models, fields, _


class HrJob(models.Model):
    _inherit = "hr.job"

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.env.user.department_id
    )
