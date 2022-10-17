import base64
from secrets import choice

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.image import image_data_uri


class HrDepartment(models.Model):
    _inherit = "hr.department"

    @api.model
    def _generate_random_token(self):
        return ''.join(choice('abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789') for _i in range(10))

    @api.depends("create_date")
    def _assign_random_token(self):
        for r in self:
            r.uid = self._generate_random_token()

    uid = fields.Char(
        compute="_assign_random_token",
        copy=False,
        store=True
    )

    review_collection_id = fields.Many2one(
        comodel_name="reviews.collection",
        string="Review Form"
    )

    qr_code = fields.Char(
        string="QR Code",
        compute="_compute_qr_code",
        help="QR-Code"
    )
    qr_code_html = fields.Char(
        string="QR Code HTML",
        compute="_compute_qr_code_html",
        help="QR-Code URL"
    )

    @api.constrains("uid")
    def constrain_uid(self):
        for r in self:
            exiting_uid = self.search([("uid", "=", r.uid)])
            if len(exiting_uid) > 1:
                raise ValidationError(_("This UID Exist"))

    @api.depends('uid')
    def _compute_qr_code(self):
        for r in self:
            get_param = self.env["ir.config_parameter"].sudo().get_param
            reviews_base_url = get_param(
                "reviews.base.url") or f'{get_param("web.base.url")}/reviews'
            barcode = self.env['ir.actions.report'].barcode(
                "QR",
                f"{reviews_base_url}/{r.uid}",
                width="400",
                height="400"
            )
            qr_code = image_data_uri(base64.b64encode(barcode))
            r.qr_code = qr_code

    @api.depends('uid')
    def _compute_qr_code_html(self):
        for r in self:
            txt = _("Scan to get")
            r.qr_code_html = f'''
                        <br/>
                        <img class="border border-dark rounded" src="{self.qr_code}"/>
                        <br/>
                        <strong class="text-center">{txt}</strong>
                        '''

    def print_qr_code(self):
        if not self.review_collection_id:
            raise UserError(
                _("Please, assing 'Review Form' to print the barcode!"))

        report_template_xml_id = "reviews.report_department_review_qr_code"
        return {
            "type": "ir.actions.act_url",
            "url": f"/report/pdf/{report_template_xml_id}/{self.id}",
            "target": "new",
        }
