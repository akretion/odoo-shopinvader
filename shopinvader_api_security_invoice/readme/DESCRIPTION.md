Security rule for exposing invoices on shopinvader_api

The invoices of the authenticated partner and of its addresses (the contacts
used as invoicing addresses, see `shopinvader_address`) are exposed to the API
user: the domain of the rules uses `child_of` on the partner of the invoice.
