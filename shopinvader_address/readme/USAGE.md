InvoicingAddress  
In the context of shopinvader, the `InvoicingAddress` corresponds to the
authenticated partner itself. Once it has been replaced (see below), the
invoicing addresses are the contacts of type `invoice` of this partner.

It can be created using:

``` python
def _create_shopinvader_invoicing_address(self, vals: dict) -> "ResPartner":
```

It can be updated using:

``` python
def _update_shopinvader_invoicing_address(self, vals: dict, address_id: int) -> "ResPartner"
```

*Remark: if it has already been used on a confirmed sale order, the new values
are not written on the address: the address is replaced by a new one (see
`Address replacement` below).*

*Remark: the vat of an invoicing address is a commercial field: it always
belongs to the customer account and is written on it.*

*Remark: the vat exposed by the API is always the vat of the customer account
(`_get_shopinvader_vat_owner`): all the addresses of an account share the same
vat. The API flags it as readonly (`vat_readonly`) as soon as the account has a
confirmed sale order (`_is_shopinvader_vat_readonly`): the confirmed sale
orders must keep the fiscal data they have been validated with.*

DeliveryAddress  
In the context of shopinvader, a `DeliveryAddress` corresponds to any
delivery address linked to the authenticated partner. A partner can have
between 0 and n `DeliveryAddress`.

It can be created using:

``` python
def _create_shopinvader_delivery_address(self, vals: dict) -> "ResPartner":
```

It can be updated using:

``` python
def _update_shopinvader_delivery_address(self, vals: dict, address_id: int) -> "ResPartner":
```

It can be archived using:

``` python
def _delete_shopinvader_delivery_address(self, address: "ResPartner") -> None:
```

*Remark: the delivery addresses of a partner used on a confirmed sale order can
not be updated nor removed: they are replaced or archived (see
`Address replacement` below).*

Address replacement  
An address used on a confirmed (`sale`) or done (`done`) sale order must keep
the data it has been validated with. Such an address is never updated:

- when it is a contact of the account, it is archived;
- when it is the main partner itself, it is flagged with
  `shopinvader_address_disabled` (the account can not be archived), which
  removes it from the addresses exposed by the API.

In both cases, a new address is created with the data of the replaced one and
the new values, and the open documents (draft sale orders) of the customer are
re-assigned to this new address. The confirmed sale orders keep the replaced
address, so the documents already sent to the customer are not modified.
