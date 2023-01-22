import logging
import traceback
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..tools.odoo_rpc import OdooRPC

_logger = logging.getLogger(__name__)


class EmployeeCourses(models.Model):
    _name = "hr_learn_platform.employee_courses"
    _description = "Employee Courses"
    _rec_name = "course_id"

    course_id = fields.Many2one(
        comodel_name="hr_learn_platform.courses",
        string="Course",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
    )

    completed = fields.Boolean(
        string='Is Completed',
        default=False
    )

    # Cron Job
    @api.model
    def get_employee_course_status(self):
        """
        Cron job to update all course statuses from e-learning platform
        """
        # Get this data from settings
        try:
            get_param = self.env["ir.config_parameter"].sudo().get_param
            remote_host = get_param("e_learning_server_host")
            remote_user = get_param("e_learning_server_user")
            remote_db = get_param("e_learning_server_db")
            remote_password = get_param("e_learning_server_password")
            rpc = OdooRPC(remote_host, remote_db, remote_user, remote_password)
            partner_courses = rpc.rpc(
                "slide.channel.partner",
                "search_read",
                fields=["channel_id", "completed", "partner_id"],
                domain=[("write_date", ">", datetime.now() -
                         timedelta(days=1)), ("completed", "=", True)],
            )
            for partner_course in partner_courses:
                partner_course_id = self.search([
                    ("course_id.external_id", "=",
                     partner_course.get("channel_id")[0]),
                    ("employee_id.e_learning_partner_id", "=",
                     partner_course.get("partner_id")[0]),
                ])
                if partner_course_id:
                    partner_course_id.write({
                        "completed": True
                    })
        except Exception as ex:
            _logger.error(traceback.format_exc())
            raise UserError(_("Cannot connect to e-learning platform"))
