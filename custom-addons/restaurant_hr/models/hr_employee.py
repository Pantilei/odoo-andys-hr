import os
from odoo import api, models, fields, _
from odoo.exceptions import UserError

from datetime import datetime
import pandas as pd
import numpy as np


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.env.user.department_id
    )

    entry_date = fields.Date(
        string="Entry Date",
        default=lambda self: datetime.today()
    )

    passport_type = fields.Char(
        string="Passport Type"
    )

    passport_series = fields.Char(
        string="Passport Series"
    )

    passport_issue_date = fields.Date(
        string="Passport Issue Date"
    )

    passport_issue_by = fields.Char(
        string="Passport Issue By"
    )

    response_ids = fields.One2many(
        comodel_name="survey.user_input",
        inverse_name="employee_id",
        string="Responces",
        groups="survey.group_survey_user"
    )

    resume_pdf = fields.Binary(
        string="Resume PDF",
        groups="hr.group_hr_user",
        tracking=True
    )

    coach_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Coaches',
        # compute='_compute_coaches',
        relation="employee_coaches",
        column1="employee",
        column2="coach",
        store=True,
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" will have the opportunity to edit the information of his students.')

    functional_duty = fields.Text(
        string="Functional Duty"
    )

    payment_rate = fields.Float(
        string="Payment Rate",

    )
    # @api.depends('parent_id')
    # def _compute_coaches(self):
    #     for employee in self:
    #         manager = employee.parent_id
    #         if manager:
    #             employee.coach_ids |= manager
    #         else:
    #             employee.coach_ids = employee.coach_ids

    def assess_employee(self):
        return {
            'name': _('Select Survey'),
            'type': 'ir.actions.act_window',
            'res_model': 'restaurant_hr.employee_survey_select_wizard',
            'views': [(False, "form")],
            'context': {
                'employee_id': self.id,
            },
            'target': 'new'
        }

    def import_employee_data(self):
        Employee = self.env["hr.employee"]
        Department = self.env["hr.department"]
        Job = self.env["hr.job"]
        ceo_id = Employee.search([
            ("name", "=", "Tranga Andrei")
        ], limit=1)

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        df_employees = pd.read_csv(os.path.join(
            path, '../data/employee_data.csv')).replace({np.nan: None})

        for record in df_employees.to_dict("records"):
            # print("\n", record)
            department_id = self._get_department(
                record["Подразделение"], record["Ф.И.О."] if not record["Руководитель подразделения"] else False)
            job_id = self._get_job(record["Должность"], department_id)
            parent_id = self._get_parent(record["Руководитель подразделения"])
            address_id = self._get_address(record["Ф.И.О."], record["Адрес"])
            employee_id = Employee.search([
                ("name", "=", record["Ф.И.О."]),
                ("department_id", "=", department_id.id),
                ("job_id", "=", job_id.id)
            ], limit=1)
            if not employee_id:
                employee_id = Employee.create({
                    "name": record["Ф.И.О."],
                    "department_id": department_id.id,
                    "job_id": job_id.id,
                    "entry_date": datetime.strptime(record['Дата приема'], '%d.%m.%Y') if record['Дата приема'] else False,
                    "employee_type": "employee",
                    "parent_id": parent_id.id or ceo_id.id,
                    "identification_id": record["IDNP"],
                    "country_of_birth": 138,
                    "country_id": 138,
                    "address_home_id": address_id.id,
                    "passport_type": record["Документ тип"],
                    "passport_series": record["Документ серия"],
                    "passport_id": record["Документ номер"],
                    "passport_issue_date": datetime.strptime(record["Документ дата выдачи"], '%d.%m.%Y') if record["Документ дата выдачи"] else False,
                    "passport_issue_by": record["Документ кем выдан"],
                    "resource_calendar_id": 1
                })
            else:
                employee_id.write({
                    "name": record["Ф.И.О."],
                    "department_id": department_id.id,
                    "job_id": job_id.id,
                    "entry_date": datetime.strptime(record['Дата приема'], '%d.%m.%Y') if record['Дата приема'] else False,
                    "employee_type": "employee",
                    "parent_id": parent_id.id or ceo_id.id,
                    "identification_id": record["IDNP"],
                    "country_of_birth": 138,
                    "country_id": 138,
                    "address_home_id": address_id.id,
                    "passport_type": record["Документ тип"],
                    "passport_series": record["Документ серия"],
                    "passport_id": record["Документ номер"],
                    "passport_issue_date": datetime.strptime(record["Документ дата выдачи"], '%d.%m.%Y') if record["Документ дата выдачи"] else False,
                    "passport_issue_by": record["Документ кем выдан"],
                    "resource_calendar_id": 1
                })

    def _get_department(self, departament_name, manager_name):
        Department = self.env["hr.department"]
        Employee = self.env["hr.employee"]
        manager_id = Employee.search([
            ("name", "=", manager_name)
        ], limit=1) if manager_name else self.env["hr.employee"]
        departament_id = Department.search([
            ("name", "=", departament_name)
        ], limit=1)
        if not departament_id:
            departament_id = Department.create({
                "name": departament_name,
                "manager_id": manager_id.id
            })
        else:
            departament_id.write({
                "name": departament_name,
                "manager_id": departament_id.manager_id.id or manager_id.id
            })
        return departament_id

    def _get_job(self, job_name, department_id):
        Job = self.env["hr.job"]
        job_id = Job.search([
            ("name", "=", job_name),
            ("department_id", "=", department_id.id)
        ], limit=1)
        if not job_id:
            job_id = Job.create({
                "name": job_name,
                "department_id": department_id.id,
                "state": "open",
                "no_of_recruitment": 0
            })
        else:
            job_id.write({
                "name": job_name,
                "department_id": department_id.id,
                "state": "open",
                "no_of_recruitment": 0
            })
        return job_id

    def _get_parent(self, parent_name):
        Employee = self.env["hr.employee"]
        employee_id = Employee.search([
            ("name", "=", parent_name),
        ], limit=1)
        return employee_id

    def _get_address(self, name, address_info):
        Address = self.env["res.partner"]
        if not address_info:
            return Address
        address_data = address_info.split(",")
        city = False
        street = False
        if len(address_data) >= 1:
            city = address_data[0]
            street = ",".join(address_data[1:])
        if len(address_data) < 1:
            street = ",".join(address_data)
        address_id = Address.search([
            ("name", "=", name)
        ], limit=1)

        if not address_id:
            address_id = Address.create({
                "name": name,
                "country_id": 138,
                "street": street,
                "city": city,
                "lang": "ru_RU"
            })

        return address_id
