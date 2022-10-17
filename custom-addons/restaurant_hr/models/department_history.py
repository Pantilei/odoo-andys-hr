from odoo import models, api, fields, _


class DepartmentHistory(models.Model):
    _name = "restaurant_hr.department_history"
    _description = "Department History"

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        required=True
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True
    )

    status = fields.Selection(
        selection=[
            ("enter", "Enter"),
            ("exit", "Exit"),
        ],
        default="entered",
        required=True
    )

    history_date = fields.Datetime(
        string="History Date",
        required=True
    )
