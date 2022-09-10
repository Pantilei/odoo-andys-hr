from odoo import models, api, fields, _


class AvailableHrJobNames(models.Model):
    _name = "restaurant_hr.available_hr_job_names"
    _description = "Available HR Job Names"

    name = fields.Char(
        required=True
    )
