import werkzeug
import string
import traceback
import logging
from secrets import choice

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ..tools.odoo_rpc import OdooRPC


_logger = logging.Logger(__name__)


class EmployeeAssignManyCourses(models.TransientModel):
    _name = "hr_learn_platform.employee_assign_many_courses"
    _description = "Employee assign many courses"

    def _default_employee_assigment(self):
        employee_ids = self.env.context.get("employee_ids")
        return [(0, 0, {
            "employee_id": employee_id,
        }) for employee_id in employee_ids]

    employee_assigment_ids = fields.One2many(
        comodel_name="hr_learn_platform.employee_assign_course",
        inverse_name="employee_assign_many_course_id",
        default=_default_employee_assigment
    )

    course_id = fields.Many2one(
        comodel_name="hr_learn_platform.courses",
        string="Course",
        required=True
    )

    def confirm(self):
        try:
            # Get this data from settings
            get_param = self.env["ir.config_parameter"].sudo().get_param
            remote_host = get_param("e_learning_server_host")
            remote_user = get_param("e_learning_server_user")
            remote_db = get_param("e_learning_server_db")
            remote_password = get_param("e_learning_server_password")
            rpc = OdooRPC(remote_host, remote_db, remote_user, remote_password)
            for line in self.employee_assigment_ids:
                res = rpc.rpc(
                    "slide.channel",
                    "create_assign_user_to_course",
                    line.employee_name, line.personal_id, line.password, self.course_id.external_id
                )
                remote_user_id = res.get("user_id")
                remote_partner_id = res.get("partner_id")
                EmployeeCourses = self.env["hr_learn_platform.employee_courses"]
                employee_course_id = EmployeeCourses.search([
                    ("course_id", "=", self.course_id.external_id),
                    ("employee_id", "=", line.employee_id.id),
                    ("e_learning_user_id", "=", remote_user_id),
                ])
                if not employee_course_id:
                    self.env["hr_learn_platform.employee_courses"].create({
                        "course_id": self.course_id.external_id,
                        "employee_id": line.employee_id.id,
                        "e_learning_user_id": remote_user_id,
                        "e_learning_partner_id": remote_partner_id
                    })
                else:
                    employee_course_id.write({
                        "course_id": self.course_id.external_id,
                        "employee_id": line.employee_id.id,
                        "e_learning_user_id": remote_user_id,
                        "e_learning_partner_id": remote_partner_id
                    })
                line.employee_id.write({
                    "access_to_e_learning": True
                })

        except Exception as ex:
            _logger.error(traceback.format_exc())
            raise UserError(
                _("Cannot connect to e-learning platform! Please contact your administrator!")) from ex


class EmployeeAssignCourse(models.TransientModel):
    _name = "hr_learn_platform.employee_assign_course"
    _description = "Employee Assign Course Wizard"

    def _random_password(self):
        return ''.join([choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _i in range(5)])

    @api.depends("employee_id")
    def _compute_persanal_id(self):
        for record in self:
            record.personal_id = f"{record.employee_id.id:06d}"

    employee_assign_many_course_id = fields.Many2one(
        comodel_name="hr_learn_platform.employee_assign_many_courses"
    )

    password = fields.Char(
        string="Password",
        default=_random_password
    )

    employee_name = fields.Char(
        string="Employee Name",
        related="employee_id.name"
    )

    personal_id = fields.Char(
        string="ID/Login",
        compute="_compute_persanal_id",
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee"
    )
