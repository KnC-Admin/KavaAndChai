# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class pos_session(models.Model):
    _inherit = 'pos.session'

    @api.model
    def create(self,vals):
        res = super(pos_session, self).create(vals)
        res.branch_id = res.config_id.branch_id.id
        return res

    branch_id = fields.Many2one('res.branch', 'Branch')

class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self,vals):
        res = super(pos_order, self).create(vals)
        res.branch_id = res.session_id.branch_id.id
        return res

    branch_id = fields.Many2one('res.branch', 'Branch')

    # def _create_account_move(self, dt, ref, journal_id, company_id):
    #     account_move = super(pos_order, self)._create_account_move(dt, ref, journal_id, company_id)
    #     account_move.branch_id = self.session_id.branch_id or False
    #     print("\n--------Journal created",self.session_id.branch_id)
    #     return account_move


    # # Overwritten by codisoft: to add branch_id to stock_picking and stock_move
    # def create_picking(self):
    #     """Create a picking for each order and validate it."""
    #     Picking = self.env['stock.picking']
    #     Move = self.env['stock.move']
    #     StockWarehouse = self.env['stock.warehouse']
    #     for order in self:
    #         if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
    #             continue
    #         address = order.partner_id.address_get(['delivery']) or {}
    #         picking_type = order.picking_type_id
    #         return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
    #         order_picking = Picking
    #         return_picking = Picking
    #         moves = Move
    #         location_id = order.location_id.id
    #         if order.partner_id:
    #             destination_id = order.partner_id.property_stock_customer.id
    #         else:
    #             if (not picking_type) or (not picking_type.default_location_dest_id):
    #                 customerloc, supplierloc = StockWarehouse._get_partner_locations()
    #                 destination_id = customerloc.id
    #             else:
    #                 destination_id = picking_type.default_location_dest_id.id
    #
    #         if picking_type:
    #             message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
    #             picking_vals = {
    #                 'origin': order.name,
    #                 'partner_id': address.get('delivery', False),
    #                 'date_done': order.date_order,
    #                 'branch_id': order.branch_id and order.branch_id.id or False,
    #                 'picking_type_id': picking_type.id,
    #                 'company_id': order.company_id.id,
    #                 'move_type': 'direct',
    #                 'note': order.note or "",
    #                 'location_id': location_id,
    #                 'location_dest_id': destination_id,
    #             }
    #             pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
    #             if pos_qty:
    #                 order_picking = Picking.create(picking_vals.copy())
    #                 order_picking.message_post(body=message)
    #             neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
    #             if neg_qty:
    #                 return_vals = picking_vals.copy()
    #                 return_vals.update({
    #                     'location_id': destination_id,
    #                     'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
    #                     'picking_type_id': return_pick_type.id
    #                 })
    #                 return_picking = Picking.create(return_vals)
    #                 return_picking.message_post(body=message)
    #
    #         for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding)):
    #             moves |= Move.create({
    #                 'name': line.name,
    #                 'product_uom': line.product_id.uom_id.id,
    #                 'branch_id': order.branch_id and order.branch_id.id or False,
    #                 'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
    #                 'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_qty': abs(line.qty),
    #                 'state': 'draft',
    #                 'location_id': location_id if line.qty >= 0 else destination_id,
    #                 'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
    #             })
    #
    #         # prefer associating the regular order picking, not the return
    #         order.write({'picking_id': order_picking.id or return_picking.id})
    #
    #         if return_picking:
    #             order._force_picking_done(return_picking)
    #         if order_picking:
    #             order._force_picking_done(order_picking)
    #
    #         # when the pos.config has no picking_type_id set only the moves will be created
    #         if moves and not return_picking and not order_picking:
    #             moves._action_assign()
    #             moves.filtered(lambda m: m.state in ['confirmed', 'waiting']).force_assign()
    #             moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()
    #     print("\n--------------Picking created")
    #     return True

class pos_config(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', 'Branch')


    @api.multi
    @api.constrains('branch_id','stock_location_id')
    def _check_branch_constrains(self):
        if self.branch_id and self.stock_location_id:
            if self.branch_id.id != self.stock_location_id.branch_id.id:
                raise UserError(_('Configuration error\nYou  must select same branch on a location as asssigned on a point of sale configuration.'))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
