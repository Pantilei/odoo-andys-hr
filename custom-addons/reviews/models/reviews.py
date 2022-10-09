from odoo import models, fields, api, _


class Reviews(models.Model):
    _name = 'reviews'
    _description = 'Reviews'
    _order = "create_date desc"

    name = fields.Char(
        string="Name"
    )
    phone = fields.Char(
        string="Phone"
    )
    email = fields.Char(
        string="Email"
    )
    responsible_name = fields.Char(
        string="Employee Name"
    )
    responsible_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Related Employee"
    )
    description = fields.Text(
        string="Description"
    )

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
    )
