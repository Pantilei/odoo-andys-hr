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

    course_ids = fields.Many2many(
        comodel_name="hr_learn_platform.courses",
        relation="hr_learn_pltfm_crs_hr_learn_p_employee_assign_courses_rel",
        string="Courses",
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
                for course_id in self.course_ids:
                    res = rpc.rpc(
                        "slide.channel",
                        "create_assign_user_to_course",
                        line.employee_name, line.personal_id, line.password, course_id.external_id
                    )
                    remote_user_id = res.get("user_id")
                    remote_partner_id = res.get("partner_id")
                    EmployeeCourses = self.env["hr_learn_platform.employee_courses"]
                    employee_course_id = EmployeeCourses.search([
                        ("course_id", "=", course_id.id),
                        ("employee_id", "=", line.employee_id.id),
                    ])
                    if not employee_course_id:
                        self.env["hr_learn_platform.employee_courses"].create({
                            "course_id": course_id.id,
                            "employee_id": line.employee_id.id,
                        })
                    else:
                        employee_course_id.write({
                            "course_id": course_id.id,
                            "employee_id": line.employee_id.id,
                        })
                    line.employee_id.write({
                        "access_to_e_learning": True,
                        "e_learning_user_id": remote_user_id,
                        "e_learning_partner_id": remote_partner_id
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

    @api.depends("e_learning_user_id")
    def _compute_random_password(self):
        for record in self:
            if record.e_learning_user_id == 0:
                record.password = self._random_password()
            else:
                record.password = False

    @api.depends("employee_id")
    def _compute_personal_id(self):
        for record in self:
            record.personal_id = f"{record.employee_id.id:06d}"

    def _set_password(self):
        pass

    @api.depends("e_learning_user_id")
    def _compute_in_e_learning_system(self):
        for record in self:
            record.in_e_learning_system = bool(record.e_learning_user_id)

    employee_assign_many_course_id = fields.Many2one(
        comodel_name="hr_learn_platform.employee_assign_many_courses"
    )

    password = fields.Char(
        string="Password",
        compute="_compute_random_password",
        inverse="_set_password",
        store=True
    )

    employee_name = fields.Char(
        string="Employee Name",
        related="employee_id.name"
    )

    personal_id = fields.Char(
        string="ID/Login",
        compute="_compute_personal_id",
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee"
    )

    e_learning_user_id = fields.Integer(
        related="employee_id.e_learning_user_id"
    )

    in_e_learning_system = fields.Boolean(
        string="In E-Leaning System",
        compute="_compute_in_e_learning_system"
    )
