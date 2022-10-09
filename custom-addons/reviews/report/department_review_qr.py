from odoo import fields, models, api


class QRCodeReviews(models.AbstractModel):
    _name = 'report.reviews.report_department_review_qr_code'
    _description = 'Reviews QR Code'

    def _get_report_values(self, doc_id, data=None):
        doc = self.env['hr.department'].browse(doc_id)
        return {
            'doc_model': 'hr.department',
            'doc': doc,
            'qr_code': doc.qr_code
        }
