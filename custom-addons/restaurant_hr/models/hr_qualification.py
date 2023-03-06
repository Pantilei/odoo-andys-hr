from odoo import _, api, fields, models


class HrQualification(models.Model):
    _name = "restaurant_hr.qualification"
    _description = "Qualification"

    name = fields.Char(
        string="Name",
        required=True
    )

    branch_id = fields.Many2one(
        comodel_name="restaurant_hr.hr_branch",
        string="Branch"
    )
