from odoo import _, fields, models


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

    staff_size = fields.Integer(
        string="Staff Size",
        default=0
    )

    def org_chart_department(self):
        org_chart_id = self.env["restaurant_hr.hr_dep_org_chart"].create({
            "department_id": self.id,
        })
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "restaurant_hr.hr_dep_org_chart",
            'res_id': org_chart_id.id,
            "views": [[False, "form"]],
            "target": "current"
        }
