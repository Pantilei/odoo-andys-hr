from odoo import models, api, fields, _


class EmployeeAchievements(models.Model):
    _name = "restaurant_hr.employee_achievements"
    _description = "HR Employee Achievents"
    _order = "assigment_date desc"

    description = fields.Text(
        string="Name",
        required=True
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        index=True
    )

    assigment_date = fields.Date(
        string="Date",
        required=True
    )
