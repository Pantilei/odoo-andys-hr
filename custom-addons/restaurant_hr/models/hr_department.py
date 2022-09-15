from odoo import models, fields, api, _


class HrDepartment(models.Model):
    _inherit = "hr.department"

    _order = "sequence"

    sequence = fields.Integer(
        string='Sequence',
        default=10,
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
