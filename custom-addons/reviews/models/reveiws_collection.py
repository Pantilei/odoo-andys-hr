import string
from secrets import choice

from odoo import models, api, fields, _


class ReviewsCollection(models.Model):
    _name = "reviews.collection"
    _description = "Reviews Collection"

    @api.model
    def _generate_random_token(self):
        return ''.join(choice('abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789') for _i in range(10))

    name = fields.Char(
        string="Name"
    )

    phone = fields.Char(
        string="Support Phone"
    )

    email = fields.Char(
        string="Support Email"
    )

    bg_img = fields.Image(
        string="Background Image"
    )
