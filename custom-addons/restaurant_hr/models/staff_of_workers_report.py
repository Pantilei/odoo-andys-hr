from calendar import monthrange
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class StaffOfWorkersReport(models.TransientModel):
    _name = "restaurant_hr.staff_of_workers_report"
    _description = "Staff of Workers Report"

    name = fields.Char(
        string="Name",
        default="Отчет по штату"
    )

    period = fields.Selection(
        selection=[
            ("current_month", "Current Month"),
            ("previous_month", "Previous Month"),
            ("last_3_months", "Last 3 Months"),
        ],
        string="Period",
        default="current_month",
        required=True
    )

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        required=True
    )

    branch_id = fields.Many2one(
        comodel_name="restaurant_hr.hr_branch",
        string="Branch",
        required=True
    )

    staff_line_ids = fields.Many2many(
        comodel_name="restaurant_hr.staff_of_workers_line",
        string="Staff",
        compute="_compute_staff_lines"
    )

    @api.depends("period", "department_id", "branch_id", )
    def _compute_staff_lines(self):
        HrDepartment = self.env["hr.department"]
        HrEmployee = self.env["hr.employee"]
        HrJob = self.env["hr.job"]
        for record in self:
            if not record.period or not record.department_id or not record.branch_id:
                record.staff_line_ids = []
                continue
            start_date, end_date = self._get_dates_from_period(record.period)
            all_department_ids = HrDepartment.search([("id", "child_of", record.department_id.id)])
            record.staff_line_ids = [(0, 0, {
                "department_id": child_department_id.id,
                "staff_count": 0,
                "staff_actual_count": len(HrEmployee.search([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "employee"),
                    ("branch_id", "=", record.branch_id.id),
                ])),
                "open_position_count": sum(HrJob.search([
                    ("department_id", "child_of", child_department_id.id),
                    ("branch_id", "=", record.branch_id.id),
                    ("state", "=", "recruit")
                ]).mapped("no_of_recruitment")),
                "trainee_count": len(HrEmployee.search([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "trainee"),
                    ("branch_id", "=", record.branch_id.id),
                    ("training_start_date", ">=", start_date),
                    "|",
                    ("training_end_date", "<=", end_date),
                    ("training_end_date", "=", False),
                ])),
                "dismissed_count": len(HrEmployee.with_context(active_test=True).search([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "employee"),
                    ("branch_id", "=", record.branch_id.id),
                    ("active", "=", False),
                    ("departure_date", ">=", start_date),
                    ("departure_date", "<=", end_date),
                ])),
                "hired_count": len(HrEmployee.search([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "employee"),
                    ("branch_id", "=", record.branch_id.id),
                    ("active", "=", True),
                    ("entry_date", ">=", start_date),
                    ("entry_date", "<=", end_date)
                ])),
            }) for child_department_id in all_department_ids]

    def _get_dates_from_period(self, period):
        today = date.today()
        if period == "current_month":
            return date(year=today.year, month=today.month, day=1), today
        if period == "previous_month":
            one_month_before = today - relativedelta(months=-1)
            week_day, days = monthrange(year=one_month_before.year, month=one_month_before.month)
            return (
                date(year=one_month_before.year, month=one_month_before.month, day=1), 
                date(year=one_month_before.year, month=one_month_before.month, day=days)
            )
        if period == "last_3_months":
            tree_months_before = today - relativedelta(months=-3)
            week_day, days = monthrange(year=tree_months_before.year, month=tree_months_before.month)
            return (
                date(year=tree_months_before.year, month=tree_months_before.month, day=1), 
                date(year=tree_months_before.year, month=tree_months_before.month, day=days)
            )


class StaffOfWorkersReportLine(models.TransientModel):
    _name = "restaurant_hr.staff_of_workers_line"
    _description = "staff_of_workers_line"

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department"
    )
    staff_count = fields.Integer()
    staff_actual_count = fields.Integer()
    open_position_count = fields.Integer()
    trainee_count = fields.Integer()
    dismissed_count = fields.Integer()
    hired_count = fields.Integer()
