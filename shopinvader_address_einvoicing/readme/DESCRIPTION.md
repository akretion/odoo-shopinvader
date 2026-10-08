This addon exposes the French eInvoicing directory of the customer on the
addresses managed by the Shopinvader API:

* the company identifier of the customer account (``company_identifier``, the
  SIRET used to query the French eInvoicing directory),
* the directory line selected by default on the address
  (``einvoicing_directory_line``),
* a service to sync the directory from the front end when the customer encodes
  its SIRET,
* a flag on the countries exposed by the settings service to know if the French
  eInvoicing applies.
