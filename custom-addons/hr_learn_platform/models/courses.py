import logging
import traceback

from ..tools.odoo_rpc import OdooRPC
from odoo import api, models, fields, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class Courses(models.Model):
    _name = "hr_learn_platform.courses"
    _description = "Courses"

    name = fields.Char()
    external_id = fields.Integer(
        string="External ID"
    )
    active = fields.Boolean(
        default=True
    )

    # Cron Job
    @api.model
    def get_remote_courses(self):
        """
        Cron job to update all courses from e-learning platform
        """
        try:
            # Get this data from settings
            get_param = self.env["ir.config_parameter"].sudo().get_param
            remote_host = get_param("e_learning_server_host")
            remote_user = get_param("e_learning_server_user")
            remote_db = get_param("e_learning_server_db")
            remote_password = get_param("e_learning_server_password")
            rpc = OdooRPC(remote_host, remote_db, remote_user, remote_password)
            courses = rpc.rpc(
                "slide.channel",
                "search_read",
                fields=["name", "channel_type"]
            )
            old_course_ids = self.search([])
            for course in courses:
                print(course)
                course_id = self.search(
                    [("external_id", "=", course.get("id"))])
                old_course_ids -= course_id
                if course_id:
                    course_id.write({
                        "name": course.get("name")
                    })
                else:
                    course_id = self.create({
                        "name": course.get("name"),
                        "external_id": course.get("id")
                    })
            old_course_ids.write({
                "active": False
            })
        except Exception as ex:
            _logger.error(traceback.format_exc())
            raise UserError(_("Cannot connect to E-Learning Platform!"))
