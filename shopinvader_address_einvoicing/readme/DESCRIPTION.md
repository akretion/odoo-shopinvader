This addon exposes the French eInvoicing directory of the customer on the
addresses managed by the Shopinvader API:

* the directory line selected by default on the address
  (``default_fr_directory_line_id``) and the directory lines of the customer
  account (``fr_directory_line_ids``),
* a service to sync the directory from the front end when the customer
  encodes its vat number,
* a flag on the countries exposed by the settings services to know if the
  French eInvoicing applies.
