import werkzeug
import json

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from datetime import date, datetime
from calendar import monthrange

from odoo import models, fields, api, _


def short_date(dt):
    a = dt.strftime('%m/%Y').split('/')
    return "/".join([a[0], a[1][2:]])


class DepartmentHistoryReportWizard(models.TransientModel):
    _name = "restaurant_hr.department_history_report_wizard"
    _description = "Department History Report Wizard"

    def _default_date_start(self):
        d = date.today() + relativedelta(months=-6)
        return date(
            year=d.year,
            month=d.month,
            day=1
        )

    def _default_date_end(self):
        d = date.today()
        return date(
            year=d.year,
            month=d.month,
            day=monthrange(d.year, d.month)[1]
        )

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        required=True,
        index=True
    )

    date_start = fields.Date(
        string="Date Start",
        required=True,
        default=_default_date_start,
        index=True
    )

    date_end = fields.Date(
        string="Date End",
        required=True,
        default=_default_date_end,
        index=True
    )

    chart_json = fields.Text(
        string="Chart JSON",
        compute="_compute_chart_json"
    )

    @api.depends("department_id", "date_start", "date_end")
    def _compute_chart_json(self):
        for record in self:
            if not record.department_id or not record.date_start or not record.date_end:
                record.chart_json = json.dumps({
                    'type': 'bar',
                    'data': {
                        'labels': [0],
                        'datasets': [{
                            'type': 'bar',
                            'label': _("Enter"),
                            'data': [0],
                            'borderColor': 'rgb(255, 99, 132)',
                            'backgroundColor': 'rgb(255, 99, 132, 0.5)',
                        }, {
                            'type': 'bar',
                            'label': _("Exit"),
                            'data': [0],
                            'borderColor': 'rgb(96, 186, 125)',
                            'backgroundColor': 'rgb(96, 186, 125, 0.5)',
                        }]
                    },
                    'options': record._get_chart_options(),
                })
                return
            month_range = [r for r in
                           rrule(MONTHLY, dtstart=record.date_start, until=record.date_end)]
            month_range_str = [short_date(r) for r in month_range]
            grouped_data = self.env["restaurant_hr.department_history"].read_group(
                domain=[
                    ("department_id", "=", record.department_id.id),
                    ("history_date", ">", record.date_start),
                    ("history_date", "<=", record.date_end),
                ],
                fields=["department_id"],
                groupby=["history_date:month", "status"],
                lazy=False
            )
            enter_data = [0 for _i in month_range]
            exit_data = [0 for _i in month_range]

            for i, m in enumerate(month_range):
                for g in grouped_data:
                    to_date = datetime.strptime(
                        g["__range"]["history_date"]["to"], "%Y-%m-%d %H:%M:%S")
                    if m.year == to_date.year and m.month == to_date.month:
                        if g.get("status") == "enter":
                            enter_data[i] = g["__count"]
                        if g.get("status") == "exit":
                            exit_data[i] = g["__count"]

            record.chart_json = json.dumps({
                'type': 'bar',
                'data': {
                    'labels': month_range_str,
                    'datasets': [{
                        'type': 'bar',
                        'label': _("Enter"),
                        'data': enter_data,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgb(255, 99, 132, 0.5)',
                    }, {
                        'type': 'bar',
                        'label': _("Exit"),
                        'data': exit_data,
                        'borderColor': 'rgb(96, 186, 125)',
                        'backgroundColor': 'rgb(96, 186, 125, 0.5)',
                    }]
                },
                'options': record._get_chart_options(),
            })

    def _get_chart_options(self):
        return {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'position': 'top',
                },
                'title': {
                    'display': True,
                    'text': _("Employee Enter/Exit count!")
                }
            },
            'scales': {
                'xAxes': [{
                    'display': True,
                    'scaleLabel': {
                        'display': True,
                        'labelString': _('Months')
                    }
                }],
                'yAxes': [{
                    'display': True,
                    'ticks': {
                        'suggestedMin': 0,
                    },
                    'scaleLabel': {
                        'display': True,
                        'labelString': _('Count')
                    }
                }]
            }
        }
