from odoo import models, fields, api, _


class HrDepartment(models.Model):
    _inherit = "hr.department"

    _order = "sequence"

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
