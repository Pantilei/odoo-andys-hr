import os
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from ..tools.odoo_rpc import OdooRPC

import traceback
import logging


_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    course_ids = fields.One2many(
        comodel_name="hr_learn_platform.employee_courses",
        inverse_name="employee_id",
        string="Courses"
    )

    access_to_e_learning = fields.Boolean(
        string="Access to E-Learning"
    )

    show_close_access_to_e_learning = fields.Boolean(
        compute="_compute_show_close_access_to_e_learning"
    )

    @api.depends("course_ids")
    def _compute_show_close_access_to_e_learning(self):
        for record in self:
            record.show_close_access_to_e_learning = len(
                record.course_ids) != 0 and record.access_to_e_learning

    def assign_to_course(self):
        if not self.work_email:
            raise UserError(
                _("Please, give the work email to employee before assigning the course!"))

        return {
            "name": _("Select Course"),
            "type": "ir.actions.act_window",
            "res_model": "hr_learn_platform.employee_assign_course",
            "views": [(False, "form")],
            "context": {
                "employee_id": self.id,
            },
            "target": "new"
        }

    def close_access_to_e_learning(self):
        remote_user_ids = self.course_ids.mapped("e_learning_user_id")
        if len(remote_user_ids) != 1:
            raise UserError(
                _(f"Multiple users in e-learning platform related with same employee. User ids: {remote_user_ids}"))
        remote_user_id = remote_user_ids[0]
        try:

            get_param = self.env["ir.config_parameter"].sudo().get_param
            remote_host = get_param("e_learning_server_host")
            remote_user = get_param("e_learning_server_user")
            remote_db = get_param("e_learning_server_db")
            remote_password = get_param("e_learning_server_password")
            rpc = OdooRPC(remote_host, remote_db, remote_user, remote_password)
            rpc.rpc(
                "res.users",
                "write",
                [remote_user_id],
                {
                    "active": False
                },
            )
            self.access_to_e_learning = False
        except Exception as ex:
            _logger.error(traceback.format_exc())
            raise UserError(_("Cannot connect to e-learning platform")) from ex
