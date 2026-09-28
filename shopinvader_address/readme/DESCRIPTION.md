This addons adds helper methos on the res.partner model that ease the
management and the creation of addresses within odoo code.

An address (delivery or invoicing) used on a confirmed or done sale order must
keep the data it has been validated with: it can not be updated nor deleted.

Such an address is then *replaced* by a new one:

* the address is archived, or flagged with ``shopinvader_address_disabled`` when
  it is the main partner of the account, as the account itself can not be
  archived,
* a new address is created with the data of the replaced one and the new values,
* the open documents (draft sale orders: carts, quotations) of the customer are
  re-assigned to the new address, the confirmed ones keep the replaced address.
