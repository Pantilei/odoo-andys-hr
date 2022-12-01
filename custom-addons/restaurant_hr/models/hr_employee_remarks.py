from odoo import models, api, fields, _


class EmployeeRemarks(models.Model):
    _name = "restaurant_hr.employee_remarks"
    _description = "HR Employee Remarks"
    _order = "assigment_date desc"

    description = fields.Text(
        string="Description",
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
