# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api

class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_product_pack = fields.Boolean('Allow Modifiers', default=True)


class ProductGroups(models.Model):
    _name = 'product.pack.group'

    name = fields.Char(translate=True)

class fix_product_pack(models.Model):
    _name = 'fix.product.pack'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
        vals['price_unit'] = self.product_id.lst_price

        result = {'domain': domain}
        self.update(vals)
        return result

    @api.onchange('product_uom', 'qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        product = self.product_id.with_context(quantity=self.qty,uom=self.product_uom.id)
        self.price_unit = product.lst_price


    product_id = fields.Many2one('product.product','Product', required=1)
    product_ids = fields.Many2one('product.product','Product')
    qty = fields.Float("Quantity",default=1,required=1)
    product_uom = fields.Many2one("product.uom", "Unit of Measure")
    price_unit = fields.Float("Unit Price")

class selective_product_pack(models.Model):
    _name = 'selective.product.pack'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
        vals['price_unit'] = self.product_id.lst_price

        result = {'domain': domain}
        self.update(vals)
        return result

    @api.onchange('product_uom', 'qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        product = self.product_id.with_context(quantity=self.qty, uom=self.product_uom.id)
        self.price_unit = product.lst_price

    product_id = fields.Many2one('product.product','Product',required=1)
    product_ids = fields.Many2one('product.product','Product')
    default_selected = fields.Boolean('Default selected')
    qty = fields.Float("Quantity",default=1,required=1)
    product_uom = fields.Many2one("product.uom", "Unit of Measure")
    price_unit = fields.Float("Unit Price")
    group_id = fields.Many2one('product.pack.group', string='Group',required=1)

class product_product(models.Model):
    _inherit = 'product.product'
    
    is_pack = fields.Boolean('has BOM')
    is_fix_pack = fields.Boolean('Fixed Components', default=True)
    is_selective_pack = fields.Boolean('Modifier Components')
    item_limit = fields.Integer("Modifier Components limit")
    fix_pack_id = fields.One2many('fix.product.pack','product_ids',string="Fixed Components")
    selective_pack_id = fields.One2many('selective.product.pack','product_ids',string="Modifier Components")

    
class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _order_fields(self, ui_order):
        new_lines = []
        if 'lines' in ui_order:
            for lines in ui_order['lines']:
                new_lines.append(lines)
                if 'selected_product_list' in lines[2]:
                    for selected_pack in lines[2]['selected_product_list']:
                        # print('\n--------selected product = ',selected_pack)
                        new_lines.append(selected_pack)
                if 'fixed_product_list' in lines[2]:
                    for fixed_pack in lines[2]['fixed_product_list']:
                        # print('\n--------fix product = ', fixed_pack)
                        new_lines.append(fixed_pack)
            ui_order['lines'] = new_lines
        return super(PosOrder, self)._order_fields(ui_order)



