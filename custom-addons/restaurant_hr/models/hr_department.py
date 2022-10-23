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
        default="medium",
        help="""
            If department is the restaurant, you can specify its size, the salaries of certain employees will 
            depend on it.
        """
    )

    def org_chart_department(self):
        return {
            "name": _("Org Chart"),
            "type": "ir.actions.act_window",
            "res_model": "restaurant_hr.hr_dep_org_chart",
            "context": {
                "default_department_id": self.id
            },
            'view_mode': 'form',
            "views": [[False, "form"]],
            "target": "current"
        }
