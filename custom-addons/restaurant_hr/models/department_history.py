from odoo import _, api, fields, models


class DepartmentHistory(models.Model):
    _name = "restaurant_hr.department_history"
    _description = "Department History"

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        index=True,
        ondelete="set null",
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        index=True,
        ondelete="set null",
    )

    branch_id = fields.Many2one(
        comodel_name="restaurant_hr.hr_branch",
        string="Branch",
        index=True,
        ondelete="set null",
        related="employee_id.branch_id",
        store=True
    )

    status = fields.Selection(
        selection=[
            ("enter", "Enter"),
            ("exit", "Exit"),
        ],
        default="enter",
        index=True,
        required=True
    )

    history_date = fields.Datetime(
        string="History Date",
        required=True,
        index=True,
    )
