import os
from odoo import api, models, fields, _
from odoo.exceptions import UserError

from datetime import datetime
import pandas as pd
import numpy as np
import logging


_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = ['res.users']

    branch_id = fields.Many2one(
        related='employee_id.branch_id', readonly=False, related_sudo=False)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.env.user.department_id
    )

    job_id = fields.Many2one(
        'hr.job', 'Job Position',
        domain="[('department_id', 'child_of', department_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]"
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

    assessed = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Assessed",
        compute="_compute_assessed"
    )

    resume_pdf = fields.Binary(
        string="Resume PDF",
        groups="hr.group_hr_user",
        tracking=True
    )

    source_id = fields.Many2one(
        comodel_name="utm.source",
        string="Source"
    )

    branch_id = fields.Many2one(
        comodel_name='restaurant_hr.hr_branch',
        string='Branch',
        help='Select the "Branch" to whom this employee belongs.\n'
             'The manager of branch will have the opportunity to edit the information of this employee.')

    qualification_id = fields.Many2one(
        comodel_name='restaurant_hr.qualification',
        string='Qualification'
    )

    functional_duty = fields.Text(
        string="Functional Duty"
    )

    payment_rate = fields.Float(
        string="Payment Rate",

    )

    wage_rate_min = fields.Float(
        string="Wage Rate Min",
        compute="_compute_wage_rate"
    )
    wage_rate_max = fields.Float(
        string="Wage Rate Max",
        compute="_compute_wage_rate"
    )

    personal_id = fields.Char(
        string="Personal ID",
        compute="_compute_persanal_id"
    )

    @api.depends("create_date")
    def _compute_persanal_id(self):
        for record in self:
            record.personal_id = f"{record.id:06d}"

    @api.depends("response_ids")
    def _compute_assessed(self):
        for record in self:
            record.assessed = "yes" if record.response_ids.filtered(
                lambda r: r.state == "done") else "no"

    @api.depends('response_ids')
    def _compute_wage_rate(self):
        for employee in self:
            sorted_response_ids = employee.response_ids.sorted(
                key=lambda r: r.create_date, reverse=True)
            if not sorted_response_ids:
                employee.wage_rate_max = 0
                employee.wage_rate_min = 0
                continue
            last_response_id = sorted_response_ids[0]
            if last_response_id.survey_id.survey_group == "cook":
                wage_rate_cook_ids = last_response_id.survey_id.wage_rate_cook_medium_department_ids
                if employee.department_id.department_size == "small":
                    wage_rate_cook_ids = last_response_id.survey_id.wage_rate_cook_small_department_ids
                elif employee.department_id.department_size == "medium":
                    wage_rate_cook_ids = last_response_id.survey_id.wage_rate_cook_medium_department_ids
                elif employee.department_id.department_size == "large":
                    wage_rate_cook_ids = last_response_id.survey_id.wage_rate_cook_large_department_ids
                wage_rate_max = 0
                wage_rate_min = 0
                for line in wage_rate_cook_ids:
                    if line.scoring_from <= last_response_id.scoring_percentage/100 <= line.scoring_to:
                        wage_rate_max = line.wage_rate_max
                        wage_rate_min = line.wage_rate_min
                employee.wage_rate_max = wage_rate_max
                employee.wage_rate_min = wage_rate_min

            elif last_response_id.survey_id.survey_group == "waiter":
                oldest_to_newest_waiter_response_ids = employee.response_ids\
                    .filtered(lambda r: r.survey_id.survey_group == "waiter")\
                    .sorted(key=lambda r: r.create_date)

                per_survey_rate = {}
                for waiter_response_id in oldest_to_newest_waiter_response_ids:
                    r_max = 0
                    r_min = 0
                    for line in waiter_response_id.survey_id.wage_rate_waiter_ids:
                        if line.scoring_from < waiter_response_id.scoring_percentage/100 <= line.scoring_to:
                            r_min = line.wage_rate_min
                            r_max = line.wage_rate_max
                    per_survey_rate.update({
                        waiter_response_id.survey_id.id: {
                            "max_rate": r_max,
                            "min_rate": r_min,
                        }
                    })

                max_rates = sum([k["max_rate"]
                                for k in per_survey_rate.values()])
                min_rates = sum([k["min_rate"]
                                for k in per_survey_rate.values()])
                employee.wage_rate_max = max_rates
                employee.wage_rate_min = min_rates
            else:
                employee.wage_rate_max = 0
                employee.wage_rate_min = 0

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

    @api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        rec_ids = super(HrEmployee, self).create(vals_list)
        for rec_id in rec_ids:
            if rec_id.department_id:
                rec_id._create_department_history(
                    rec_id.department_id, status="enter")
        return rec_ids

    def write(self, vals):
        self.clear_caches()
        initial_department_id = self.department_id
        res = super(HrEmployee, self).write(vals)
        final_department_id = self.department_id
        if initial_department_id != final_department_id:
            self._create_department_history(
                final_department_id, status="enter")
            self._create_department_history(
                initial_department_id, status="exit")
        if "active" in vals:
            if vals.get("active"):
                self._create_department_history(
                    final_department_id, status="enter")
            else:
                self._create_department_history(
                    final_department_id, status="exit")
        return res

    def unlink(self):
        self.clear_caches()
        self._create_department_history(self.department_id, status="exit")
        return super(HrEmployee, self).unlink()

    def _create_department_history(self, department_id, status="enter"):
        self.env["restaurant_hr.department_history"].create([{
            "department_id": department_id.id,
            "employee_id": self.id,
            "status": status,
            "history_date": self.create_date
        }])

    # DATA IMPORT
    def import_employee_data2(self):
        Employee = self.env["hr.employee"]
        Department = self.env["hr.department"]
        Job = self.env["hr.job"]
        ceo_id = Employee.search([
            ("name", "=", "Tranga Andrei")
        ], limit=1)

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        df_employees = pd.read_csv(os.path.join(
            path, '../data/employee_data.csv'), dtype=str).replace({np.nan: None})

        for record in df_employees.to_dict("records"):
            print("\n", record)
            department_id = Department.search([
                ("name", "=", record["Подразделение"])
            ], limit=1)
            if not department_id:
                raise UserError("Cannot find department!")
            job_id = self._get_job(record["Должность"], department_id)
            parent_id = department_id.manager_id
            address_id = self._get_address(
                record["Фамилия, имя"], record["Адрес"])
            employee_id = Employee.search([
                ("name", "=", record["Фамилия, имя"]),
            ], limit=1)
            passport_series, passport_id = record["Серия Номер Паспорта"].split(
                " ")
            if not employee_id:

                employee_id = Employee.create({
                    "name": record["Фамилия, имя"],
                    "department_id": department_id.id,
                    "job_id": job_id.id,
                    "entry_date": datetime.strptime(record['Дата оформления'], '%d.%m.%Y %H:%M:%S') if record['Дата оформления'] else False,
                    "employee_type": "employee",
                    "parent_id": parent_id.id,
                    "identification_id": record["Фиск код"],
                    "country_of_birth": 138,
                    "country_id": 138,
                    "address_home_id": address_id.id,
                    "passport_type": "Buletin de identitate al cetat.RM",
                    "passport_series": passport_series,
                    "passport_id": passport_id,
                    "gender": record["Пол"],
                    "resource_calendar_id": 1
                })
            else:
                employee_id.write({
                    "name": record["Фамилия, имя"],
                    "department_id": department_id.id,
                    "job_id": job_id.id,
                    "entry_date": datetime.strptime(record['Дата оформления'], '%d.%m.%Y %H:%M:%S') if record['Дата оформления'] else False,
                    "employee_type": "employee",
                    "parent_id": parent_id.id,
                    "identification_id": record["Фиск код"],
                    "country_of_birth": 138,
                    "country_id": 138,
                    "address_home_id": address_id.id,
                    "passport_type": "Buletin de identitate al cetat.RM",
                    "passport_series": passport_series,
                    "passport_id": passport_id,
                    "gender": record["Пол"],
                    "resource_calendar_id": 1
                })

    def import_employee_data(self):
        Employee = self.env["hr.employee"]
        Department = self.env["hr.department"]
        Job = self.env["hr.job"]
        ceo_id = Employee.search([
            ("name", "=", "Tranga Andrei")
        ], limit=1)

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        df_employees = pd.read_csv(os.path.join(
            path, '../data/employee_data.csv'), dtype=str).replace({np.nan: None})

        for record in df_employees.to_dict("records"):
            print("\n", record)
            department_id = self._get_department(
                record["Подразделение"],
                record["Ф.И.О."] if not record["Руководитель подразделения"] else False,
                record["Название Сети"]
            )
            job_id = self._get_job(record["Должность"], department_id)
            parent_id = self._get_parent(record["Руководитель подразделения"])
            address_id = self._get_address(record["Ф.И.О."], record["Адрес"])
            employee_id = Employee.search([
                ("name", "=", record["Ф.И.О."]),
                # ("department_id", "=", department_id.id),
                # ("job_id", "=", job_id.id)
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

    def _get_department(self, departament_name, manager_name, network_name=None):
        Department = self.env["hr.department"]
        Employee = self.env["hr.employee"]

        network_department_id = self.env["hr.department"]
        if network_name:
            network_department_id = Department.search([
                ("name", "=", network_name)
            ])
            if not network_department_id:
                network_department_id = Department.create({
                    "name": network_name
                })
            else:
                network_department_id.write({
                    "name": network_name,
                })

        manager_id = Employee.search([
            ("name", "=", manager_name)
        ], limit=1) if manager_name else self.env["hr.employee"]
        departament_id = Department.search([
            ("name", "=", departament_name)
        ], limit=1)
        if not departament_id:
            departament_id = Department.create({
                "name": departament_name,
                "manager_id": manager_id.id,
                "parent_id": network_department_id.id
            })
        else:
            departament_id.write({
                "name": departament_name,
                "manager_id": departament_id.manager_id.id or manager_id.id,
                "parent_id": network_department_id.id
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

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self.env.is_superuser():
    #         return super(HrEmployee, self)._search(domain, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    #     if not self.env.user.has_group("hr.group_hr_user"):
    #         raise AccessError(
    #             _("You don't have the rights to view employees."))
    #     final_domain = domain
    #     if self.env.user.has_group("hr.group_hr_user") and not self._context.get('search_all_employees', None):
    #         final_domain = expression.AND([
    #             domain,
    #             ['&', '|',
    #              ('department_id', 'child_of', self.env.user.department_id.id),
    #              ('branch_id', 'child_of', self.env.user.branch_id.id),
    #              ('id', '!=', self.env.user.employee_id.id)
    #              ]
    #         ])
    #     if self.env.user.has_group("hr.group_hr_manager"):
    #         final_domain = domain
    #     return super(HrEmployee, self)._search(final_domain, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    # @api.model
    # def search_panel_select_range(self, field_name, search_domain=None, **kwargs):
    #     if self.env.is_superuser():
    #         return super(HrEmployee, self).search_panel_select_range(field_name, search_domain=final_domain, **kwargs)
    #     if not self.env.user.has_group("hr.group_hr_user"):
    #         raise AccessError(
    #             _("You don't have the rights to view employees."))
    #     final_domain = search_domain
    #     if self.env.user.has_group("hr.group_hr_user") and not self._context.get('search_all_employees', None):
    #         final_domain = expression.AND([
    #             search_domain,
    #             ['&', '|',
    #              ('department_id', 'child_of', self.env.user.department_id.id),
    #              ('branch_id', 'chlld_of', self.env.user.branch_id.id),
    #              ('id', '!=', self.env.user.employee_id.id)
    #              ]
    #         ])
    #     if self.env.user.has_group("hr.group_hr_manager"):
    #         final_domain = search_domain
    #     return super(HrEmployee, self).search_panel_select_range(field_name, search_domain=final_domain, **kwargs)
