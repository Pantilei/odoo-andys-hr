import werkzeug
import string
import traceback
import logging
from secrets import choice

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ..tools.odoo_rpc import OdooRPC


_logger = logging.Logger(__name__)


class EmployeeAssignCourse(models.TransientModel):
    _name = "hr_learn_platform.employee_assign_course"
    _description = "Employee Assign Course Wizard"

    def _random_password(self):
        return ''.join([choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _i in range(10)])

    course_id = fields.Many2one(
        comodel_name="hr_learn_platform.courses",
        string="Course",
        required=True
    )
    password = fields.Char(
        string="Password",
        default=_random_password
    )

    employee_name = fields.Char(
        string="Employee Name",
        related="employee_id.name"
    )

    email = fields.Char(
        string="Email/Login",
        related="employee_id.work_email"
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        default=lambda self: self.env.context.get("employee_id")
    )

    def confirm(self):
        # Get this data from settings
        try:
            get_param = self.env["ir.config_parameter"].sudo().get_param
            remote_host = get_param("e_learning_server_host")
            remote_user = get_param("e_learning_server_user")
            remote_db = get_param("e_learning_server_db")
            remote_password = get_param("e_learning_server_password")
            rpc = OdooRPC(remote_host, remote_db, remote_user, remote_password)
            res = rpc.rpc(
                "slide.channel",
                "create_assign_user_to_course",
                self.employee_name, self.email, self.password, self.course_id.external_id
            )
            remote_user_id = res.get("user_id")
            remote_partner_id = res.get("partner_id")
            EmployeeCourses = self.env["hr_learn_platform.employee_courses"]
            employee_course_id = EmployeeCourses.search([
                ("course_id", "=", self.course_id.external_id),
                ("employee_id", "=", self.employee_id.id),
                ("e_learning_user_id", "=", remote_user_id),
            ])
            print("\n\n RES", res)
            if not employee_course_id:
                self.env["hr_learn_platform.employee_courses"].create({
                    "course_id": self.course_id.external_id,
                    "employee_id": self.employee_id.id,
                    "e_learning_user_id": remote_user_id,
                    "e_learning_partner_id": remote_partner_id
                })
            else:
                employee_course_id.write({
                    "course_id": self.course_id.external_id,
                    "employee_id": self.employee_id.id,
                    "e_learning_user_id": remote_user_id,
                    "e_learning_partner_id": remote_partner_id
                })
            self.employee_id.write({
                "access_to_e_learning": True
            })

        except Exception as ex:
            _logger.error(traceback.format_exc())
            raise UserError(
                _("Cannot connect to e-learning platform! Please contact your administrator!")) from ex
