# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_datetime, formatLang, get_lang


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def get_products_price_backportedv16(self, products, quantity, uom=None, date=False,  **kwargs):
        return self._get_products_price_backportedv16(products, quantity, uom, date, **kwargs)

    def _get_products_price_backportedv16(self, products, quantity, uom=None, date=False,  **kwargs):
        """ For a given pricelist, return price for products
        Returns: dict{product_id: product price}, in the given pricelist """
        self.ensure_one()
        return {
            product_id: res_tuple[0]
            for product_id, res_tuple in self._compute_price_rule_backportedv16(
                products,
                quantity,
                uom=uom,
                date=date,
                 **kwargs,
            ).items()
        }


    def _get_product_price_backportedv16(self, product, quantity, uom=None, date=False,  **kwargs):
        """ For a given pricelist, return price for a given product """
        self.ensure_one()
        return self._compute_price_rule_backportedv16(product, quantity, uom=uom, date=date, **kwargs)[product.id][0]

    def _get_product_price_rule_backportedv16(self, product, quantity, uom=None, date=False, **kwargs):
        """ For a given pricelist, return price and rule for a given product """
        self.ensure_one()
        return self._compute_price_rule_backportedv16(product, quantity, uom=uom, date=date, **kwargs)[product.id]

    def _compute_price_rule_backportedv16(self, products, qty, uom=None, date=False,  **kwargs):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        :param products: recordset of products (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
            If not specified, prices returned are expressed in product uoms
        :param date: date to use for price computation and currency conversions
        :type date: date or datetime

        :returns: product_id: (price, pricelist_rule)
        :rtype: dict
        """
        self.ensure_one()

        if not products:
            return {}

        if not date:
            # Used to fetch pricelist rules and currency rates
            date = fields.Datetime.now()

        # Fetch all rules potentially matching specified products/templates/categories and date
        rules = self._get_applicable_rules_backportedv16(products, date)

        if 'currency' in products.env.context:
            # Remove currency from product context to avoid any
            # side-effect currency conversion in price_compute calls
            # since we manage currency conversion without the context fallbacks
            # raph osef
            pass
            # product = products.with_context(currency=False)

        results = {}
        for product in products:
            suitable_rule = self.env['product.pricelist.item']

            product_uom = product.uom_id
            target_uom = uom or product_uom  # If no uom is specified, fall back on the product uom

            # Compute quantity in product uom because pricelist rules are specified
            # w.r.t product default UoM (min_quantity, price_surchage, ...)
            if target_uom != product_uom:
                qty_in_product_uom = target_uom._compute_quantity(qty, product_uom, raise_if_failure=False)
            else:
                qty_in_product_uom = qty

            for rule in rules:
                if rule._is_applicable_for_backportedv16(product, qty_in_product_uom):
                    suitable_rule = rule
                    break

            kwargs['pricelist'] = self
            price = suitable_rule._compute_price_backportedv16(product, qty, target_uom, date=date, currency=self.currency_id, base_price=None)

            results[product.id] = (price, suitable_rule.id)

        return results

    # Split methods to ease (community) overrides
    def _get_applicable_rules_backportedv16(self, products, date, **kwargs):
        self.ensure_one()
        # Do not filter out archived pricelist items, since it means current pricelist is also archived
        # We do not want the computation of prices for archived pricelist to always fallback on the Sales price
        # because no rule was found (thanks to the automatic orm filtering on active field)
        # raph
        # return self.env['product.pricelist.item'].with_context(active_test=False).search(
        try:
            self.__class__.cache_rules
        except AttributeError:
            self.__class__.cache_rules = {}

        global_cache = self.__class__.cache_rules
        this_cache = global_cache.setdefault("%s %s" % (self.id, date), {})

        tmplates = products.mapped('product_tmpl_id')

        #clefs : self, products + date
        
        domain = self._get_applicable_rules_domain_backportedv16(products=tmplates, date=date, **kwargs)
        results = self.env['product.pricelist.item'].browse(False)
        fromdb = False
        # todo refliter per product_id ?
        for product in products:            
            if product.id not in this_cache.keys():
                if not fromdb:
                    fromdb = self.env['product.pricelist.item'].search(domain)
                this_cache[product.id] = fromdb
            results |= this_cache[product.id]
        return results

    def _get_applicable_rules_domain_backportedv16(self, products, date, *kwargs):
        if products._name == 'product.template':
            templates_domain = ('product_tmpl_id', 'in', products.ids)
            products_domain = ('product_id.product_tmpl_id', 'in', products.ids)
        else:
            templates_domain = ('product_tmpl_id', 'in', products.product_tmpl_id.ids)
            products_domain = ('product_id', 'in', products.ids)


        return [
            ('pricelist_id', '=', self.id),
            '|', ('categ_id', '=', False), ('categ_id', 'parent_of', products.categ_id.ids),
            '|', ('product_tmpl_id', '=', False), templates_domain,
            '|', ('product_id', '=', False), products_domain,
            '|', ('date_start', '=', False), ('date_start', '<=', date),
            '|', ('date_end', '=', False), ('date_end', '>=', date),
        ]


    # Multi pricelists price|rule computation
    def _price_get_backportedv16(self, product, qty, **kwargs):
        """ Multi pricelist, mono product - returns price per pricelist """
        return {
            key: price[0]
            for key, price in self._compute_price_rule_multi_backportedv16(product, qty, **kwargs)[product.id].items()}

    def _compute_price_rule_multi_backportedv16(self, products, qty, uom=None, date=False, **kwargs):
        """ Low-level method - Multi pricelist, multi products
        Returns: dict{product_id: dict{pricelist_id: (price, suitable_rule)} }"""
        if not self.ids:
            pricelists = self.search([])
        else:
            pricelists = self
        results = {}
        for pricelist in pricelists:
            subres = pricelist._compute_price_rule_backportedv16(products, qty, uom=uom, date=date, **kwargs)
            for product_id, price in subres.items():
                results.setdefault(product_id, {})
                results[product_id][pricelist.id] = price
        return results

    def _get_partner_pricelist_multi_search_domain_hook_backportedv16(self, company_id):
        return [
            ('active', '=', True),
            ('company_id', 'in', [company_id, False]),
        ]

    def _get_partner_pricelist_multi_filter_hook_backportedv16(self):
        return self.filtered('active')

    # res.partner.property_product_pricelist field computation
    @api.model
    def _get_partner_pricelist_multi_backportedv16(self, partner_ids):
        """ Retrieve the applicable pricelist for given partners in a given company.

        It will return the first found pricelist in this order:
        First, the pricelist of the specific property (res_id set), this one
                is created when saving a pricelist on the partner form view.
        Else, it will return the pricelist of the partner country group
        Else, it will return the generic property (res_id not set), this one
                is created on the company creation.
        Else, it will return the first available pricelist

        :param int company_id: if passed, used for looking up properties,
            instead of current user's company
        :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive users. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)
        company_id = self.env.company.id

        Property = self.env['ir.property'].with_company(company_id)
        Pricelist = self.env['product.pricelist']
        pl_domain = self._get_partner_pricelist_multi_search_domain_hook_backportedv16(company_id)

        # if no specific property, try to find a fitting pricelist
        result = Property._get_multi('property_product_pricelist', Partner._name, partner_ids)

        remaining_partner_ids = [pid for pid, val in result.items() if not val or
                                 not val._get_partner_pricelist_multi_filter_hook_backportedv16()]
        if remaining_partner_ids:
            # get fallback pricelist when no pricelist for a given country
            pl_fallback = (
                Pricelist.search(pl_domain + [('country_group_ids', '=', False)], limit=1) or
                Property._get('property_product_pricelist', 'res.partner') or
                Pricelist.search(pl_domain, limit=1)
            )
            # group partners by country, and find a pricelist for each country
            domain = [('id', 'in', remaining_partner_ids)]
            groups = Partner.read_group(domain, ['country_id'], ['country_id'])
            for group in groups:
                country_id = group['country_id'] and group['country_id'][0]
                pl = Pricelist.search(pl_domain + [('country_group_ids.country_ids', '=', country_id)], limit=1)
                pl = pl or pl_fallback
                for pid in Partner.search(group['__domain']).ids:
                    result[pid] = pl

        return result


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _is_applicable_for_backportedv16(self, product, qty_in_product_uom):
        """Check whether the current rule is valid for the given product & qty.
        Note: self.ensure_one()
        :param product: product record (product.product/product.template)
        :param float qty_in_product_uom: quantity, expressed in product UoM
        :returns: Whether rules is valid or not
        :rtype: bool
        """
        self.ensure_one()
        product.ensure_one()
        res = True

        is_product_template = product._name == 'product.template'
        if self.min_quantity and qty_in_product_uom < self.min_quantity:
            res = False

        elif self.categ_id:
            # Applied on a specific category
            cat = product.categ_id
            while cat:
                if cat.id == self.categ_id.id:
                    break
                cat = cat.parent_id
            if not cat:
                res = False
        else:
            # Applied on a specific product template/variant
            if is_product_template:
                if self.product_tmpl_id and product.id != self.product_tmpl_id.id:
                    res = False
                elif self.product_id and not (
                    product.product_variant_count == 1
                    and product.product_variant_id.id == self.product_id.id
                ):
                    # product self acceptable on template if has only one variant
                    res = False
            else:
                if self.product_tmpl_id and product.product_tmpl_id.id != self.product_tmpl_id.id:
                    res = False
                elif self.product_id and product.id != self.product_id.id:
                    res = False

        return res


  
    def _compute_price_backportedv16(self, product, quantity, uom, date, currency=None, base_price=None):
        """Compute the unit price of a product in the context of a pricelist application.

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param currency: pricelist currency (for the specific case where self is empty)
        
        :returns: price according to pricelist rule, expressed in pricelist currency
        :rtype: float
        """

        product.ensure_one()
        uom.ensure_one()
        currency = currency or self.currency_id
        currency.ensure_one()
        # Pricelist specific values are specified according to product UoM
        # and must be multiplied according to the factor between uoms
        product_uom = product.uom_id
        if product_uom != uom:
            convert = lambda p: product_uom._compute_price(p, uom)
        else:
            convert = lambda p: p

        if self.compute_price == 'fixed':
            price = convert(self.fixed_price)
        elif self.compute_price == 'percentage':
            if not base_price:
                base_price = self._compute_base_price_backportedv16(product, quantity, uom, date, currency)
            price = (base_price - (base_price * (self.percent_price / 100))) or 0.0
        elif self.compute_price == 'formula':
            if not base_price:
                base_price = self._compute_base_price_backportedv16(product, quantity, uom, date, currency)
            # complete formula
            price_limit = base_price
            price = (base_price - (base_price * (self.price_discount / 100))) or 0.0
            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            if self.price_surcharge:
                price += convert(self.price_surcharge)

            if self.price_min_margin:
                price = max(price, price_limit + convert(self.price_min_margin))

            if self.price_max_margin:
                price = min(price, price_limit + convert(self.price_max_margin))
        else:  # empty self, or extended pricelist price computation logic
            price = self._compute_base_price_backportedv16(product, quantity, uom, date, currency)


        return price

    def _compute_base_price_backportedv16(self, product, quantity, uom, date, target_currency):
        """ Compute the base price for a given rule

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param target_currency: pricelist currency

        :returns: base price, expressed in pricelist currency
        :rtype: float
        """
        rule_base = self.base
        if rule_base == 'pricelist' and self.base_pricelist_id:
            price = self.base_pricelist_id._get_product_price_backportedv16(
                product, quantity, uom, date)
            src_currency = self.base_pricelist_id.currency_id
        elif rule_base == "standard_price":
            #dead code, no product.price_compute_backported yet
            src_currency = product.cost_currency_id
            price = product.price_compute_backportedv16(rule_base, uom=uom, date=date)[product.id]
        else: # list_price
            #dead code, no product.price_compute_backported yet
            src_currency = product.currency_id
            price = product.price_compute_backportedv16(rule_base, uom=uom, date=date)[product.id]

        if src_currency != target_currency:
            price = src_currency._convert(price, target_currency, self.env.company, date, round=False)

        return price

   

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    def _get_contextual_price_backportedv16(self):
        self.ensure_one()
        return self.product_tmpl_id._get_contextual_price_backportedv16(self)
    
    def price_compute_backportedv16(self, price_type, uom=None, currency=None, company=None, date=False):
        company = company or self.env.company
        date = date or fields.Date.context_today(self)

        self = self.with_company(company)
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            self = self.sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in self:
            # TODO: bug dans odoo? price_type = null if pricelist.item = False
            # https://github.com/odoo/odoo/pull/109443
            price = product[price_type] if price_type or 0.0
            price_currency = product.currency_id
            if price_type == 'standard_price':
                price_currency = product.cost_currency_id

            if price_type == 'list_price':
                price += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    price += sum(self._context.get('no_variant_attributes_price_extra'))

            if uom:
                price = product.uom_id._compute_price(price, uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                price = price_currency._convert(price, currency, company, date)

            prices[product.id] = price

        return prices

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    def _get_contextual_price_backportedv16(self, product=None):
        self.ensure_one()
        # YTI TODO: During website_sale cleaning, we should get rid of those crappy context thing
        pricelist = self._get_contextual_pricelist_backportedv16()
        if not pricelist:
            return 0.0

        quantity = self.env.context.get('quantity', 1.0)
        uom = self.env['uom.uom'].browse(self.env.context.get('uom'))
        date = self.env.context.get('date')
        return pricelist._get_product_price_backportedv16(product or self, quantity, uom=uom, date=date)

    def _get_contextual_pricelist_backportedv16(self):
        """ Get the contextual pricelist
        This method is meant to be overriden in other standard modules.
        """
        if self._context.get('pricelist'):
            return self.env['product.pricelist'].browse(self._context.get('pricelist'))
        return self.env['product.pricelist']

    def price_compute_backportedv16(self, price_type, uom=None, currency=None, company=None, date=False):
        company = company or self.env.company
        date = date or fields.Date.context_today(self)

        self = self.with_company(company)
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            self = self.sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for template in self:
            price = template[price_type] or 0.0
            price_currency = template.currency_id
            if price_type == 'standard_price':
                price_currency = template.cost_currency_id

            # yes, there can be attribute values for product template if it's not a variant YET
            # (see field product.attribute create_variant)
            if price_type == 'list_price' and self._context.get('current_attributes_price_extra'):
                # we have a list of price_extra that comes from the attribute values, we need to sum all that
                price += sum(self._context.get('current_attributes_price_extra'))

            if uom:
                price = template.uom_id._compute_price(price, uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                price = price_currency._convert(price, currency, company, date)

            prices[template.id] = price
        return prices


# patch sans tout changer:
# #
#     product = product.with_context(**product_context)
#         pricelist = pricelist.with_context(**product_context) if pricelist else None
#         # If we have a pricelist, use product.price as it already accounts
#         # for pricelist rules and quantity (in context)
#         if False:
#             price_unit = product._get_contextual_price_backportedv16() if pricelist else product.lst_price
#         else:
#             price_unit = product.price if pricelist else product.lst_price
#         price_unit = AccountTax._fix_tax_included_price_company(
#             price_unit, product.taxes_id, taxes, company
#         )
#         res = {
#             "value": price_unit,
#             "tax_included": any(tax.price_include for tax in taxes),
#             # Default values in case price.discount_policy != "without_discount"
#             "original_value": price_unit,
#             "discount": 0.0,
#         }
#         # Handle pricelists.discount_policy == "without_discount"
#         if pricelist and pricelist.discount_policy == "without_discount":
#             # Get the price rule
#             # ici raph
#             if False:
#                 _logger.info('v16')
#                 price_unit, rule_id = pricelist._get_product_price_rule_backportedv16(
#                     product, qty, None, date=date
#                 )
#             else:
#                 price_unit, rule_id = pricelist.get_product_price_rule(
#                     product, qty, None, date=date
#                 )
#             # Get the price before applying the pricelist
#             SaleOrderLine = self.env["sale.order.line"].with_context(**product_context)
#             original_price_unit, currency = SaleOrderLine._get_real_price_currency(
#                 product, rule_id, qty, product.uom_id, pricelist.id
#             )

#             price_unit = product.price if pricelist else product.lst_price
#         price_unit = AccountTax._fix_tax_included_price_company(
#             price_unit, product.taxes_id, taxes, company
#         )
#         res = {
#             "value": price_unit,
#             "tax_included": any(tax.price_include for tax in taxes),
#             # Default values in case price.discount_policy != "without_discount"
#             "original_value": price_unit,
#             "discount": 0.0,
#         }
#         # Handle pricelists.discount_policy == "without_discount"
#         if pricelist and pricelist.discount_policy == "without_discount":
#             # Get the price rule
#             # ici raph
#             if False:
#                 _logger.info('v16')
#                 price_unit, rule_id = pricelist._get_product_price_rule_backportedv16(
#                     product, qty, None, date=date
#                 )
#             else:
#                 price_unit, rule_id = pricelist.get_product_price_rule(
#                     product, qty, None, date=date
#                 )
#             # Get the price before applying the pricelist
#             SaleOrderLine = self.env["sale.order.line"].with_context(**product_context)
#             original_price_unit, currency = SaleOrderLine._get_real_price_currency(
#                 product, rule_id, qty, product.uom_id, pricelist.id
#             )
