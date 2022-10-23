import json
from tkinter import E

from odoo import models, api, fields, _


class HrDepOrgChart(models.TransientModel):
    _name = "restaurant_hr.hr_dep_org_chart"
    _description = "HR Department Org Chart"
    _rec_name = "department_id"

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        required=True
    )

    chart_json = fields.Text(
        string="Chart Json",
        compute="_compute_chart_json"
    )

    @api.depends("department_id")
    def _compute_chart_json(self):
        Department = self.env["hr.department"]
        Employee = self.env["hr.employee"]

        for record in self:
            if not record.department_id:
                continue
            manager_id = record.department_id.manager_id
            data = [{
                "id": f"{manager_id.id}",
                "name": manager_id.name,
                "imageUrl": self._get_image(manager_id.id),
                "parentId": "",
                "positionName": manager_id.job_id.name,
            }]

            department_employee_ids = Employee.search([
                ("department_id", "child_of", record.department_id.id)
            ])
            job_ids = department_employee_ids.mapped(
                "job_id") - manager_id.job_id
            for job_id in job_ids:
                job_employee_ids = Employee.search([
                    ("department_id", "child_of", record.department_id.id),
                    ("job_id", "=", job_id.id)
                ])
                data.append({
                    "id": f"job_{job_id.id}",
                    "name": job_id.name,
                    "imageUrl": None,
                    "parentId": f"{manager_id.id}",
                    "positionName": None,
                })
                data.extend([{
                    "id": f"{e.id}",
                    "name": e.name,
                    "imageUrl": self._get_image(e.id),
                    "parentId": f"job_{job_id.id}",
                    "positionName": e.job_id.name,
                } for e in job_employee_ids])

            manager_of_manager_id = record.department_id.manager_id.parent_id
            if manager_of_manager_id:
                data[0]["parentId"] = f"{manager_of_manager_id.id}"
                data.insert(0, {
                    "id": f"{manager_of_manager_id.id}",
                    "name": manager_of_manager_id.name,
                    "imageUrl": self._get_image(manager_of_manager_id.id),
                    "parentId": None,
                    "positionName": manager_of_manager_id.job_id.name,
                })
            record.chart_json = json.dumps(data)

    def _get_image(self, emp_id):
        return f"/web/image/hr.employee.public/{emp_id}/image_1024"
