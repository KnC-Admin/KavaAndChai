odoo.define('pos_pro_pack.pos_pro_pack', function (require) {
"use strict";

var models = require('point_of_sale.models');
var chrome = require('point_of_sale.chrome');
var core = require('web.core');
var PosPopWidget = require('point_of_sale.popups');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var gui = require('point_of_sale.gui');
var screens = require('point_of_sale.screens');
var _t = core._t;

models.load_fields('product.product',['is_pack','is_fix_pack','is_selective_pack','fixed_selective_pack','item_limit','fix_pack_id','selective_pack_id']);

models.load_models([{
        model: 'fix.product.pack',
        condition: function(self){ return self.config.allow_product_pack; },
        fields: ['product_id','qty','product_uom','price_unit'],
        loaded: function(self,result){

            if(result.length){
                self.wv_fix_pack_list = result;
            }
            else{
                self.wv_fix_pack_list = [];
            }
        },
    },{
        model: 'selective.product.pack',
        condition: function(self){ return self.config.allow_product_pack; },
        fields: ['product_id','default_selected','qty','product_uom','price_unit','group_id'],
        loaded: function(self,result){

            if(result.length){
                self.wv_selective_pack_list = result;
            }
            else{
                self.wv_selective_pack_list = [];
            }
        },
    },
    ],{'after': 'product.product'});

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            var self = this;
            OrderlineSuper.prototype.initialize.apply(this, arguments);
            
            var fix_products = false;
            if(options.product && options.product.is_pack && options.product.is_fix_pack){
                fix_products = options.product.fix_pack_id || false;
            }
            this.fix_product_ids = fix_products;

           
        },
        fixed_product_pack: function(pack_id,qty,unit){
            var self = this;
            var fixed_product = self.pos.wv_fix_pack_list;
            for(var i=0;i<fixed_product.length;i++){
                if(fixed_product[i].id == pack_id){
                    if(fixed_product[i].product_uom){
                        var unit_id = fixed_product[i].product_uom[0]
                        var unitObj = this.pos.units_by_id[unit_id]
                        unit = unitObj.name
                    }

                    return "<em>"+fixed_product[i].qty * qty+" "+unit+"</em> of "+fixed_product[i].product_id[1];
                }
            }
        },

        selected_product_pack: function(pack_id,qty,unit){
            var self = this;
            var selected_pack = self.pos.wv_selective_pack_list;
            for(var i=0;i<selected_pack.length;i++){
                if(selected_pack[i].id == pack_id){
                    if(selected_pack[i].product_uom){
                        var unit_id = selected_pack[i].product_uom[0]
                        var unitObj = this.pos.units_by_id[unit_id]
                        unit = unitObj.name
                    }
                    return "<em>"+selected_pack[i].qty * qty+" "+unit+"</em> of "+selected_pack[i].product_id[1];
                }
            }
        },
        fixed_product_pack_json: function(pack_id){
            var self = this;
            var fixed_product = self.pos.wv_fix_pack_list;
            for(var i=0;i<fixed_product.length;i++){
                if(fixed_product[i].id == pack_id){
                    return "<em>"+fixed_product[i].qty * qty+"</em> "+fixed_product[i].product_id[1];
                }
            }
        },
        selected_product_pack_json: function(pack_id){
            var self = this;
            var selected_pack = self.pos.wv_selective_pack_list;
            for(var i=0;i<selected_pack.length;i++){
                if(selected_pack[i].id == pack_id){
                    return {qty:selected_pack[i].qty * this.quantity,product_id:selected_pack[i].product_id[0],discount:0,price_unit:0};
                }
            }
        },
        fixed_product_pack_json: function(pack_id){
            var self = this;
            var fixed_product = self.pos.wv_fix_pack_list;
            for(var i=0;i<fixed_product.length;i++){
                if(fixed_product[i].id == pack_id){
                    return {qty:fixed_product[i].qty * this.quantity,product_id:fixed_product[i].product_id[0],discount:0,price_unit:0};
                }
            }
        },
        export_as_JSON: function(){
            var fixed_product_list = [];
            if(this.fix_product_ids){
                for(var i=0;i<this.fix_product_ids.length;i++){
                    fixed_product_list.push([0, 0, this.fixed_product_pack_json(this.fix_product_ids[i])]);
                }
            }
            var selected_product_list = [];
            if(this.selective_product_ids){
                for(var i=0;i<this.selective_product_ids.length;i++){
                    selected_product_list.push([0, 0, this.selected_product_pack_json(this.selective_product_ids[i])]);
                }
            }
            var data = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
            data.fixed_product_list = fixed_product_list;
            data.selected_product_list = selected_product_list;
            return data;
        }
    });

    var SelectiveProductWidget = PosPopWidget.extend({
        template: 'SelectiveProductWidget',

        renderElement: function(options){
            var self = this;
            this._super();
            this.$(".add_modifiers").click(function(){
                var selected_product_list = [];
                var extra_price = 0.0;
                $(".wv_product").each(function() {
                    if($(this).hasClass('dark-border')){
                        var product_id = $(this).data('product-id');
                        // var amount = $(this).data('product-amount');
                        extra_price = extra_price + $(this).data('product-extra');
                        selected_product_list.push(product_id);
                    }
                });
                var p_id = $('.base_product').data('product-id');
                if(p_id){
                    if(! options.edit_pack){
                        /* If it is a product pack avoid merging the product with previously selected */
                        self.pos.get_order().add_product(self.pos.db.get_product_by_id(p_id),{merge:false});
                        self.pos.get_order().selected_orderline['base_price'] = self.pos.get_order().selected_orderline.price
                    }

                    self.pos.get_order().selected_orderline['extra_price'] = extra_price
                    self.pos.get_order().selected_orderline.price = self.pos.get_order().selected_orderline.base_price + extra_price
                    self.pos.get_order().selected_orderline.selective_product_ids = selected_product_list;
                    self.pos.get_order().selected_orderline.trigger('change',self.pos.get_order().selected_orderline);
                }
                self.gui.show_screen('products');
            });
            $(".wv_product").click(function() {
                $(this).toggleClass('dark-border').siblings().removeClass('dark-border');

                /*if($(this).hasClass('dark-border')){
                    $(this).removeClass('dark-border');
                }
                else{
                    var count = 0;
                    var total = $('.base_product').data('count');
                    $(".wv_product").each(function() {
                        if($(this).hasClass('dark-border')){
                           count = count + 1;
                        }
                    });
                    if(count < total){
                        $(this).addClass('dark-border');
                    }
                    else{
                        alert("Sorry you can add only "+total+" products")
                    }
                } */          /*---------Removed limit, only one from each group: codisoft------------*/
            });
        },
        show: function(options){
            var self = this;
            this.options = options || {};
            var product_pack_list = [];

            var fixed_product_list= [];

            var grouped_selective_pack= {};
            var new_product_pack_list = [];

            var fixed_product = this.pos.wv_fix_pack_list;
            var wv_selective_pack = this.pos.wv_selective_pack_list;
            if(options.product.is_fix_pack){
                var pack_ids = options.product.fix_pack_id;
                for(var i=0;i<fixed_product.length;i++){
                    if(pack_ids.indexOf(fixed_product[i].id)>=0){
                        fixed_product_list.push(fixed_product[i]);
                    }
                }
                options.fixed_product_list = fixed_product_list;
            }
            var pack_ids = options.product.selective_pack_id;


            /*------ If editing the order take array/list of selected components--------  */
            if(options.edit_pack){
                var orderline = this.pos.get_order().selected_orderline.selective_product_ids;
            }


            for(var i=0;i<wv_selective_pack.length;i++){
                if(pack_ids.indexOf(wv_selective_pack[i].id)>=0){

                    /* If group is not Obj ,create one */
                   if(wv_selective_pack[i].group_id){
                       var group = wv_selective_pack[i].group_id[1];
                       if(!(group in grouped_selective_pack)){
                            grouped_selective_pack[group] = [];
                            }

                       /* When editing the order take the previously selected, else take the default selected */
                       if(options.edit_pack && orderline){
                            if(orderline.indexOf(wv_selective_pack[i].id)>=0){
                                    wv_selective_pack[i]['select_product'] = true;
                                }
                            else{
                                    wv_selective_pack[i]['select_product'] = false;
                            }
                       }
                       else{
                            wv_selective_pack[i]['select_product'] = wv_selective_pack[i]['default_selected'];
                       }
                       grouped_selective_pack[group].push(wv_selective_pack[i]);
                   }
                   else{
                        if(!('Components' in grouped_selective_pack)){
                            grouped_selective_pack['Components'] = [];
                            }
                        /* When editing the order take the previously selected, else take the default selected */
                        if(options.edit_pack && orderline){
                            if(orderline.indexOf(wv_selective_pack[i].id)>=0){
                                    wv_selective_pack[i]['select_product'] = true;
                                }
                            else{
                                    wv_selective_pack[i]['select_product'] = false;
                            }
                        }
                        else{
                            wv_selective_pack[i]['select_product'] = wv_selective_pack[i]['default_selected'];
                        }
                        grouped_selective_pack['Components'].push(wv_selective_pack[i]);
                   }


                    /*product_pack_list.push(wv_selective_pack[i]);*/
                }
            }


            for (var group_name in grouped_selective_pack) {
                if (grouped_selective_pack.hasOwnProperty(group_name)) {
                    /* get price of default product as group price from Obj */
                    var amount = 0.0
                    for (var k=0;k<grouped_selective_pack[group_name].length;k++){
                        if(grouped_selective_pack[group_name][k].default_selected){
                            /* Consider pricelist if any */
                            amount = (grouped_selective_pack[group_name][k].qty * grouped_selective_pack[group_name][k].price_unit).toFixed(2)
                            }
                    }
                    for (var k=0;k<grouped_selective_pack[group_name].length;k++){
                        var extra = 0.0
                        if(!(grouped_selective_pack[group_name][k].default_selected)){
                            /* Compute extra rate */
                             extra = (grouped_selective_pack[group_name][k].qty * grouped_selective_pack[group_name][k].price_unit).toFixed(2) - amount;
                            }
                        if(extra>0){
                            grouped_selective_pack[group_name][k]['extra'] = extra;

                        }
                        else{
                            grouped_selective_pack[group_name][k]['extra'] = 0.0;
                        }
                    }
                    new_product_pack_list.push({name:group_name,
                                                sel_products:grouped_selective_pack[group_name],
                                                group_amount:amount});

                }
            }
            /*options.product_pack_list = product_pack_list;
            new_product_pack_list.push(grouped_selective_pack);*/
            options.product_pack_list = new_product_pack_list;

            this._super(options); 
            this.renderElement(options);
        },
    });

    gui.define_popup({
        'name': 'selective-product-widget', 
        'widget': SelectiveProductWidget,
    });
    var OrderlineEditPackButton = screens.ActionButtonWidget.extend({
        template: 'OrderlineEditPackButton',
        button_click: function(){
            var line = this.pos.get_order().get_selected_orderline();
            if(line){
                if(line.product.is_pack && line.product.is_selective_pack){
                    this.gui.show_popup('selective-product-widget',{'product':line.product,'edit_pack':true});
                }
            }
        },
    });

    screens.define_action_button({
        'name': 'order_line_edit_pack',
        'widget': OrderlineEditPackButton,
        'condition': function(){
            return this.pos.config.allow_product_pack;
        },
    });
    screens.ProductScreenWidget.include({

        /* click_product: function(product) {
            if(product.product_variant_count <= 1){
               if(product.to_weight && this.pos.config.iface_electronic_scale){
                   this.gui.show_screen('scale',{product: product});
               }else{
                    if(this.pos.config.allow_product_pack && product.is_pack && product.is_selective_pack){
                        this.gui.show_popup('selective-product-widget',{'product':product,'edit_pack':false});
                    }
                    else{
                        this.pos.get_order().add_product(product);
                    }
                }
            }
        }, */  /*------------ Commented to use variant template */

       click_product: function(product) {
            if(this.pos.config.allow_product_pack && product.is_pack && product.is_selective_pack && product.product_variant_count <= 1){
               this.gui.show_popup('selective-product-widget',{'product':product,'edit_pack':false});
            }
            else{
                this._super(product);
            }
        },

    });
});

