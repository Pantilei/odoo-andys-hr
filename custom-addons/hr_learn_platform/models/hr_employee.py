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

    e_learning_user_id = fields.Integer(
        string="E-Learning User ID"
    )
    e_learning_partner_id = fields.Integer(
        string="E-Learning Partner ID"
    )

    @api.depends("course_ids")
    def _compute_show_close_access_to_e_learning(self):
        for record in self:
            record.show_close_access_to_e_learning = len(
                record.course_ids) != 0 and record.access_to_e_learning

    def assign_to_course(self):
        return {
            "name": _("Select Course"),
            "type": "ir.actions.act_window",
            "res_model": "hr_learn_platform.employee_assign_many_courses",
            "views": [(False, "form")],
            "context": {
                "employee_ids": self.ids,
            },
            "target": "new"
        }

    def close_access_to_e_learning(self):
        remote_user_ids = self.mapped("e_learning_user_id")
        for remote_user_id in remote_user_ids:
            try:
                get_param = self.env["ir.config_parameter"].sudo().get_param
                remote_host = get_param("e_learning_server_host")
                remote_user = get_param("e_learning_server_user")
                remote_db = get_param("e_learning_server_db")
                remote_password = get_param("e_learning_server_password")
                rpc = OdooRPC(remote_host, remote_db,
                              remote_user, remote_password)
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
                raise UserError(
                    _("Cannot connect to e-learning platform")) from ex
            
    def migrate_existing_user_photos(self):
        for employee_id in self.search([("e_learning_user_id", "!=", False)]):
            try:
                get_param = self.env["ir.config_parameter"].sudo().get_param
                remote_host = get_param("e_learning_server_host")
                remote_user = get_param("e_learning_server_user")
                remote_db = get_param("e_learning_server_db")
                remote_password = get_param("e_learning_server_password")
                rpc = OdooRPC(remote_host, remote_db,
                              remote_user, remote_password)
                rpc.rpc(
                    "res.users",
                    "write",
                    [employee_id.e_learning_user_id],
                    {
                        "image_1920": employee_id.image_1920
                    },
                )
            except Exception as ex:
                _logger.error(traceback.format_exc())
                raise UserError(
                    _("Cannot connect to e-learning platform")) from ex

