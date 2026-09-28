This addon adds pydantic schemas that represents Addresses. It
introduces InvoicingAddress and DeliveryAddress as sub classes of
Address. It has been designed and thought to be used in shopinvader
services.

Every address exposes the ``vat`` of the customer account it belongs to (the
vat is a commercial field: all the addresses of an account share the same vat)
and a ``vat_readonly`` flag, set as soon as the account has a confirmed sale
order.
