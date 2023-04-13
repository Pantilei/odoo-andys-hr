from calendar import monthrange
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class StaffOfWorkersReport(models.TransientModel):
    _name = "restaurant_hr.staff_of_workers_report"
    _description = "Staff of Workers Report"

    def _default_start_date(self):
        today = date.today()
        return date(year=today.year, month=today.month, day=1)

    def _default_end_date(self):
        today = date.today()
        return date(year=today.year, month=today.month, day=today.day)
    
    name = fields.Char(
        string="Name",
        default="Отчет по штату"
    )

    start_date = fields.Date(
        string="Start Date",
        default=_default_start_date, 
        required=True
    )
    
    end_date = fields.Date(
        string="End Date",
        default=_default_end_date,
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

    total_staff_count = fields.Integer(compute="_compute_total_counts", string="Total Staff")
    total_staff_actual_count = fields.Integer(compute="_compute_total_counts", string="Total Actual Staff")
    total_position_count = fields.Integer(compute="_compute_total_counts", string="Total Positions")
    total_trainee_count = fields.Integer(compute="_compute_total_counts", string="Total Trainees")
    total_dismissed_count = fields.Integer(compute="_compute_total_counts", string="Total Dismissed")
    total_hired_count = fields.Integer(compute="_compute_total_counts", string="Total Hired")

    @api.depends("start_date", "end_date", "department_id", "branch_id", )
    def _compute_total_counts(self):
        HrEmployee = self.env["hr.employee"]
        HrJob = self.env["hr.job"]

        for record in self:
            record.total_staff_count = sum(HrJob.search([
                ("department_id", "child_of", record.department_id.id),
                ("branch_id", "=", record.branch_id.id),
                ("state", "=", "recruit")
            ]).mapped("no_of_recruitment")) 
            
            record.total_staff_actual_count = HrEmployee.search_count([
                ("department_id", "child_of", record.department_id.id),
                ("employee_type", "=", "employee"),
                ("branch_id", "=", record.branch_id.id),
            ])

            record.total_position_count = sum(HrJob.search([
                ("department_id", "child_of", record.department_id.id),
                ("branch_id", "=", record.branch_id.id),
                ("state", "=", "recruit")
            ]).mapped("no_of_recruitment"))

            record.total_trainee_count = HrEmployee.search_count([
                ("department_id", "child_of", record.department_id.id),
                ("employee_type", "=", "trainee"),
                ("branch_id", "=", record.branch_id.id),
                ("training_start_date", ">=", record.start_date),
                "|",
                ("training_end_date", "<=", record.end_date),
                ("training_end_date", "=", False),
            ])

            record.total_dismissed_count = HrEmployee.with_context(active_test=True).search_count([
                ("department_id", "child_of", record.department_id.id),
                ("employee_type", "=", "employee"),
                ("branch_id", "=", record.branch_id.id),
                ("active", "=", False),
                ("departure_date", ">=", record.start_date),
                ("departure_date", "<=", record.end_date),
            ])

            record.total_hired_count = HrEmployee.search_count([
                ("department_id", "child_of", record.department_id.id),
                ("employee_type", "=", "employee"),
                ("branch_id", "=", record.branch_id.id),
                ("active", "=", True),
                ("entry_date", ">=", record.start_date),
                ("entry_date", "<=", record.end_date)
            ])

    @api.depends("start_date", "end_date", "department_id", "branch_id", )
    def _compute_staff_lines(self):
        HrDepartment = self.env["hr.department"]
        HrEmployee = self.env["hr.employee"]
        HrJob = self.env["hr.job"]
        for record in self:
            if not record.start_date or not record.end_date or not record.department_id or not record.branch_id:
                record.staff_line_ids = []
                continue
            
            all_department_ids = HrDepartment.search([
                ("id", "child_of", record.department_id.id)
            ])
            record.staff_line_ids = [(0, 0, {
                "department_id": child_department_id.id,
                "staff_count": sum(HrJob.search([
                    ("department_id", "child_of", child_department_id.id),
                    ("branch_id", "=", record.branch_id.id),
                    ("state", "=", "recruit")
                ]).mapped("no_of_recruitment")),
                "staff_actual_count": HrEmployee.search_count([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "employee"),
                    ("branch_id", "=", record.branch_id.id),
                ]),
                "open_position_count": sum(HrJob.search([
                    ("department_id", "child_of", child_department_id.id),
                    ("branch_id", "=", record.branch_id.id),
                    ("state", "=", "recruit")
                ]).mapped("no_of_recruitment")),
                "trainee_count": HrEmployee.search_count([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "trainee"),
                    ("branch_id", "=", record.branch_id.id),
                    ("training_start_date", ">=", record.start_date),
                    "|",
                    ("training_end_date", "<=", record.end_date),
                    ("training_end_date", "=", False),
                ]),
                "dismissed_count": HrEmployee.with_context(active_test=True).search_count([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "employee"),
                    ("branch_id", "=", record.branch_id.id),
                    ("active", "=", False),
                    ("departure_date", ">=", record.start_date),
                    ("departure_date", "<=", record.end_date),
                ]),
                "hired_count": HrEmployee.search_count([
                    ("department_id", "child_of", child_department_id.id),
                    ("employee_type", "=", "employee"),
                    ("branch_id", "=", record.branch_id.id),
                    ("active", "=", True),
                    ("entry_date", ">=", record.start_date),
                    ("entry_date", "<=", record.end_date)
                ]),
            }) for child_department_id in all_department_ids]


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
