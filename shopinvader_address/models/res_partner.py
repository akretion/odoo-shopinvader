# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import MissingError, UserError

# Fields copied from the replaced address when a new one is created. Computed
# fields are skipped: they are derived from the copied ones (e.g. the name of
# the address may be computed from the company/contact name).
SHOPINVADER_ADDRESS_FIELDS = (
    "name",
    "street",
    "street2",
    "zip",
    "city",
    "state_id",
    "country_id",
    "title",
    "phone",
    "mobile",
    "email",
    "main_shopinvader_address",
)

SHOPINVADER_INVOICING_ADDRESS_FIELDS = SHOPINVADER_ADDRESS_FIELDS + ("vat",)

# sale.order field holding the address, per Shopinvader address type
SHOPINVADER_ADDRESS_SALE_FIELD = {
    "invoicing": "partner_invoice_id",
    "delivery": "partner_shipping_id",
}

# sale.order state where the address is still free: a confirmed (sale) or done
# (done) sale order must keep the address it has been validated with.
SHOPINVADER_ADDRESS_OPEN_STATES = ("draft",)

# sale.order states where the address (and its fiscal data) is frozen
SHOPINVADER_ADDRESS_CONFIRMED_STATES = ("sale", "done")

# Fields that always belong to the customer account, never to one of its
# addresses: an address of an account may be a contact, and a contact is always
# a person. They are written on the account (see
# ``_sync_shopinvader_customer_vals``) and removed from the vals used to write
# or create the address (see ``_prepare_shopinvader_address_vals``).
SHOPINVADER_ADDRESS_ACCOUNT_FIELDS = ("company_type",)


class ResPartner(models.Model):
    _inherit = "res.partner"

    shopinvader_address_disabled = fields.Boolean(
        copy=False,
        help="Technical field. The address is not exposed anymore by the "
        "Shopinvader address API: it has been replaced by a new one and is "
        "kept for the history. A contact is archived instead, but the main "
        "partner of an account cannot be archived, hence this flag.",
    )
    main_shopinvader_address = fields.Boolean(copy=False)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _shopinvader_address_sale_field(self, address_type):
        return SHOPINVADER_ADDRESS_SALE_FIELD[address_type]

    def _is_shopinvader_address_used(self, address_type) -> bool:
        """Check if the address is used on a confirmed sale order.

        Such a sale order must keep the address it has been validated with, so
        the address can then only be *replaced* by a new one.
        """
        self.ensure_one()
        domain = [
            (self._shopinvader_address_sale_field(address_type), "=", self.id),
            ("state", "in", SHOPINVADER_ADDRESS_CONFIRMED_STATES),
        ]
        return bool(self.env["sale.order"].sudo().search(domain, limit=1))

    def _get_shopinvader_vat_owner(self) -> "ResPartner":
        """Return the partner owning the vat of the address.

        The vat is a *commercial field*: it always belongs to the commercial
        entity of the account and Odoo keeps it synchronized on the contacts
        (see ``_commercial_fields``). All the addresses of an account therefore
        share the same vat.
        """
        self.ensure_one()
        return self.commercial_partner_id

    def _is_shopinvader_vat_readonly(self) -> bool:
        """Check if the vat of the address can still be modified.

        The vat is shared by all the addresses of an account (see
        ``_get_shopinvader_vat_owner``), so the check is done on the account
        itself: as soon as it has a confirmed sale order, the vat can not be
        changed anymore, the confirmed orders must keep the fiscal data they
        have been validated with.
        """
        self.ensure_one()
        owner = self._get_shopinvader_vat_owner()
        domain = [
            ("partner_id", "=", owner.id),
            ("state", "in", SHOPINVADER_ADDRESS_CONFIRMED_STATES),
        ]
        return bool(self.env["sale.order"].sudo().search(domain, limit=1))

    def _shopinvader_address_can_be_archived(self) -> bool:
        """Check if the address can be archived.

        ``res.partner.write`` refuses to archive a partner linked to a user
        (even an archived one), such an address is flagged instead.
        """
        self.ensure_one()
        users = (
            self.env["res.users"]
            .sudo()
            .with_context(active_test=False)
            .search([("partner_id", "=", self.id)], limit=1)
        )
        return not users

    def _get_shopinvader_address_replacement_fields(self, address_type) -> list:
        """Return the fields copied from the replaced address to the new one."""
        if address_type == "invoicing":
            fields_to_copy = list(SHOPINVADER_INVOICING_ADDRESS_FIELDS)
        else:
            fields_to_copy = list(SHOPINVADER_ADDRESS_FIELDS)
        # fields added by other modules (e.g. the contact/company name)
        fields_to_copy += [f for f in ("company", "contact_name") if f in self._fields]
        return fields_to_copy

    def _get_shopinvader_address_replacement_vals(
        self, address_type, vals=None
    ) -> dict:
        """Return the vals used to create the replacement of ``self``.

        The data of the replaced address is kept (the front end only sends the
        fields it displays) and overridden by ``vals``.
        """
        self.ensure_one()
        result = {}
        for field_name in self._get_shopinvader_address_replacement_fields(
            address_type
        ):
            field = self._fields.get(field_name)
            if not field or field.compute:
                # computed values must not be copied: they are recomputed from
                # the fields copied below (and may have an inverse)
                continue
            value = self[field_name]
            if isinstance(value, models.BaseModel):
                # only the id is needed to create the new address
                value = value.id
            result[field_name] = value
        # None means "not provided": the data of the replaced address is kept.
        # This is needed for the vat of the invoicing addresses: it is always
        # part of the vals sent by the API (see InvoicingAddressUpdate).
        result.update(
            {key: val for key, val in (vals or {}).items() if val is not None}
        )
        return result

    # ------------------------------------------------------------------
    # Replacement
    # ------------------------------------------------------------------
    def _disable_shopinvader_address(self, address) -> None:
        """Remove the address from the ones exposed by the address API.

        A contact is archived (as already done for a deletion: the sale orders
        keep the reference for the history). The main partner of the account is
        the account itself: it cannot be archived, so it is flagged.
        """
        address.ensure_one()
        if address != self and address._shopinvader_address_can_be_archived():
            address.active = False
        else:
            address.shopinvader_address_disabled = True
            address.main_shopinvader_address = False

    def _reassign_shopinvader_address(self, old_address, new_address, address_type):
        """Re-assign ``old_address`` to ``new_address`` on the open documents.

        The draft sale orders (carts, quotations) of the customer must follow
        the replacement: otherwise they would keep a reference on an address
        that is not exposed anymore by the API. The validated sale orders are
        left untouched (see ``_is_shopinvader_address_used``).
        """
        self.ensure_one()
        field_name = self._shopinvader_address_sale_field(address_type)
        orders = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", self.id),
                    ("state", "in", SHOPINVADER_ADDRESS_OPEN_STATES),
                    (field_name, "=", old_address.id),
                ]
            )
        )
        if orders:
            orders.write({field_name: new_address.id})
        return orders

    def _replace_shopinvader_address(self, address_type, address, vals):
        """Replace ``address`` by a new one and return it.

        The new address is created with the data of ``address`` + ``vals``, the
        replaced one is archived (or flagged when it is the main partner) and
        the open documents are re-assigned to the new address.
        """
        self.ensure_one()
        new_vals = address._get_shopinvader_address_replacement_vals(address_type, vals)
        if address_type == "invoicing":
            new_address = self._create_shopinvader_invoicing_address(new_vals)
        else:
            new_address = self._create_shopinvader_delivery_address(new_vals)
        self._disable_shopinvader_address(address)
        self._reassign_shopinvader_address(address, new_address, address_type)
        return new_address

    # ------------------------------------------------------------------
    # Invoicing
    # ------------------------------------------------------------------
    # Invoicing addresses are the authenticated partner itself and, once
    # replaced, the contacts of type 'invoice' of this partner.

    def _is_shopinvader_invoicing_address_used(self) -> bool:
        """Check if the invoicing address is used on a confirmed sale order"""
        self.ensure_one()
        return self._is_shopinvader_address_used("invoicing")

    def _get_shopinvader_invoicing_addresses(self) -> "ResPartner":
        self.ensure_one()
        # the main partner is the invoicing address of the account, as long as
        # it has not been replaced by a dedicated contact
        addresses = self
        if self.shopinvader_address_disabled:
            addresses = self.browse()
        return addresses + self._get_shopinvader_invoicing_contacts()

    def _get_shopinvader_invoicing_contacts(self) -> "ResPartner":
        """Return the invoicing addresses of the account (its contacts of type
        ``invoice``)."""
        self.ensure_one()
        return self.env["res.partner"].search(
            [
                ("parent_id", "=", self.id),
                ("type", "=", "invoice"),
                ("shopinvader_address_disabled", "=", False),
            ]
        )

    def _get_shopinvader_invoicing_address(self, address_id: int) -> "ResPartner":
        self.ensure_one()
        addresses = self._get_shopinvader_invoicing_addresses()
        address = addresses.filtered(lambda rec: rec.id == address_id)
        if not address:
            raise MissingError(
                self.env._(
                    "Invoicing address not found, id: %(address_id)d",
                    address_id=address_id,
                )
            )
        return address

    def _create_shopinvader_invoicing_address(self, vals: dict) -> "ResPartner":
        """Create a new invoicing address as a contact of the account.

        The invoicing address used to be the authenticated partner itself.
        """
        self.ensure_one()
        # the vat and the company type can not be stored on the contact itself
        # (see _sync_shopinvader_customer_vals)
        self._sync_shopinvader_customer_vals(vals)
        vals = self._prepare_shopinvader_address_vals(vals)
        vals = dict(vals, parent_id=self.id, type="invoice")
        self.env["res.partner"].check_access("create")
        return self.env["res.partner"].sudo().create(vals)

    def _sync_shopinvader_customer_vals(self, vals) -> None:
        """Keep the customer account in sync with the data sent by the customer.

        The vat is a *commercial field* in Odoo: it belongs to the commercial
        entity (the customer account) and Odoo always synchronizes it on the
        children (see ``_commercial_fields``/``_commercial_sync_from_company``).
        It is also the one used to compute the fiscal position of the new sale
        orders (see ``_get_fiscal_position`` in ``account``), so it must be
        written on the account: an invoicing contact can not carry its own vat.

        The company type is not a commercial field: Odoo never synchronizes it
        on the children and it can be set on any partner, contact included. It
        drives the eInvoicing of the account, so it is written on the account
        too: an address of the account is always a person.
        """
        self.ensure_one()
        account_vals = {
            field_name: vals[field_name]
            for field_name in ("vat", "company_type")
            if vals.get(field_name)
        }
        if account_vals:
            self.write(account_vals)

    def _prepare_shopinvader_address_vals(self, vals) -> dict:
        """Return the vals that can be written on an address.

        The fields of ``SHOPINVADER_ADDRESS_ACCOUNT_FIELDS`` belong to the
        customer account (see ``_sync_shopinvader_customer_vals``): they are
        dropped here since the address may be a contact of the account.
        """
        return {
            field_name: value
            for field_name, value in vals.items()
            if field_name not in SHOPINVADER_ADDRESS_ACCOUNT_FIELDS
        }

    def _update_shopinvader_invoicing_address(
        self, vals: dict, address: "ResPartner"
    ) -> "ResPartner":
        self.ensure_one()
        self._sync_shopinvader_customer_vals(vals)
        vals = self._prepare_shopinvader_address_vals(vals)
        if address._is_shopinvader_invoicing_address_used():
            # the address is used on a confirmed sale order: it can not be
            # updated, a new one takes its place
            return self._replace_shopinvader_address("invoicing", address, vals)

        # Set address as main at the first update of the parent address
        if not address.main_shopinvader_address and not address.parent_id:
            vals["main_shopinvader_address"] = True

        # update_address
        address.write(vals)

        return address

    def _delete_shopinvader_invoicing_address(self, address: "ResPartner") -> None:
        """Archive (or flag) the invoicing address.

        Not exposed by the API yet (there is no DELETE route for the invoicing
        addresses) but referenced by
        ``shopinvader_api_address.routers.addresses.AddressHelper._delete_address``.
        """
        self.ensure_one()
        if address == self:
            raise UserError(
                self.env._(
                    "The invoicing address of an account can not be deleted, "
                    "create a new one instead."
                )
            )
        self._disable_shopinvader_address(address)
        new_address = self.address_get(["invoice"])["invoice"]
        if new_address == address.id:
            new_address = self.id
        self._reassign_shopinvader_address(
            address, self.env["res.partner"].browse(new_address), "invoicing"
        )

    # ---Delivery ---

    def _is_shopinvader_delivery_address_used(self) -> bool:
        """Check if the delivery address is used on a confirmed sale order"""
        self.ensure_one()
        return self._is_shopinvader_address_used("delivery")

    def _get_shopinvader_delivery_addresses(self) -> "ResPartner":
        self.ensure_one()
        domain = [
            ("type", "=", "delivery"),
            ("parent_id", "=", self.id),
            ("shopinvader_address_disabled", "=", False),
        ]

        return self.env["res.partner"].search(domain)

    def _get_shopinvader_delivery_address(self, address_id: int) -> "ResPartner":
        self.ensure_one()
        if self.id == address_id and not self.shopinvader_address_disabled:
            # as long as the account has no delivery contact, Odoo uses the
            # partner itself as delivery address (see ``address_get``)
            return self

        addresses = self._get_shopinvader_delivery_addresses()
        address = addresses.filtered(lambda rec: rec.id == address_id)
        if not address:
            raise MissingError(
                self.env._(
                    "Delivery address not found, id: %(address_id)d",
                    address_id=address_id,
                )
            )

        return address

    def _create_shopinvader_delivery_address(self, vals: dict) -> "ResPartner":
        self.ensure_one()
        # the vat and the company type can not be stored on the contact itself
        # (see _sync_shopinvader_customer_vals)
        self._sync_shopinvader_customer_vals(vals)
        vals = self._prepare_shopinvader_address_vals(vals)
        vals = dict(vals, parent_id=self.id, type="delivery")
        return self.env["res.partner"].create(vals)

    def _update_shopinvader_delivery_address(
        self, vals: dict, address: "ResPartner"
    ) -> "ResPartner":
        if any(key in vals for key in ("parent_id", "type")):
            raise UserError(
                self.env._(
                    "parent_id and type cannot be modified on"
                    " shopinvader delivery address, id: %(address_id)d",
                    address_id=address.id,
                )
            )

        self.ensure_one()

        # the vat and the company type can not be stored on the contact itself
        # (see _sync_shopinvader_customer_vals)
        self._sync_shopinvader_customer_vals(vals)
        vals = self._prepare_shopinvader_address_vals(vals)

        if address._is_shopinvader_delivery_address_used():
            # the address is used on a confirmed sale order: it can not be
            # updated, a new one takes its place
            return self._replace_shopinvader_address("delivery", address, vals)

        # update_address
        address.write(vals)
        return address

    def _delete_shopinvader_delivery_address(self, address: "ResPartner") -> None:
        """Archive (or flag) the delivery address.

        The address is not removed: a delivery address used on a confirmed sale
        order must be kept for the history. The open documents are re-assigned
        to the default delivery address of the account.
        """
        self.ensure_one()
        self._disable_shopinvader_address(address)
        new_address = self.address_get(["delivery"])["delivery"]
        if new_address == address.id:
            new_address = self.id
        self._reassign_shopinvader_address(
            address, self.env["res.partner"].browse(new_address), "delivery"
        )
