from odoo import api, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    @api.depends('job_id.name')
    def _compute_job_title(self):
        for employee in self.filtered('job_id'):
            employee.job_title = employee.job_id.name

    def update_job_titles(self):
        for record in self.search([]):
            record._compute_job_title()
