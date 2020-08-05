# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_branch_wise = True
    filter_branch = []

    @api.model
    def get_options(self, previous_options=None):
        options = super(AccountReport, self).get_options(previous_options=previous_options)
        if self.filter_branch_wise:
            self.filter_branch = [] if self.filter_branch_wise else None
        return options


    def set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = super(AccountReport,self).set_context(options)
        if options.get('branch'):
            ctx['branch_ids'] = self.env['res.branch'].browse([int(br) for br in options['branch']])  #
        return ctx
    #
    @api.multi
    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self.get_options(options)
        # apply date and date_comparison filter
        options = self.apply_date_filter(options)
        options = self.apply_cmp_filter(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic') is not None:
            searchview_dict['analytic_accounts'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.account'].search([])] or False
            searchview_dict['analytic_tags'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.tag'].search([])] or False

        branch_list = [(b.id, b.name) for b in self.env['res.branch'].search([])] or False
        if branch_list:
            searchview_dict['branch_list'] = branch_list

        report_manager = self.get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self.get_reports_buttons(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self.get_templates().get('search_template', 'account_report.search_template'),values=searchview_dict),
                }
        return info

