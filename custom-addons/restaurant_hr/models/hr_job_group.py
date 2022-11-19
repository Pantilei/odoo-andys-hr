from odoo import models, api, fields, _


class HrJobGroup(models.Model):
    _name = "restaurant_hr.hr_job_group"
    _description = "HR Job Group"

    name = fields.Char(
        required=True
    )
