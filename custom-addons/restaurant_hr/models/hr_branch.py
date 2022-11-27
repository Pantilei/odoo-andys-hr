from odoo import models, api, fields, _


class HrBranch(models.Model):
    _name = "restaurant_hr.hr_branch"
    _description = "HR Branch"

    name = fields.Char(
        string="Name",
        required=True
    )

    manager_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Branch Managers",
    )

    @api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        return super().create(vals_list)

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    def unlink(self):
        self.clear_caches()
        return super().unlink()
