from odoo import models, api, fields, _


class HrQualification(models.Model):
    _name = "restaurant_hr.qualification"
    _description = "Qualification"

    name = fields.Char(
        string="Name",
        required=True
    )
