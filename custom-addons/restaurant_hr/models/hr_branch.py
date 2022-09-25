from odoo import models, api, fields, _


class HrBranch(models.Model):
    _name = "restaurant_hr.hr_branch"
    _description = "HR Branch"

    name = fields.Char(
        string="Name",
        required=True
    )

    manager_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Branch Managers",
    )
