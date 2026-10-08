Addresses  
Every address (invoicing or delivery) exposed by the address services exposes
the French eInvoicing data of the customer account:

* ``company_identifier``: the SIRET of the customer account. It is a commercial
  data: all the addresses of an account share the same one and it is the value
  used to query the French eInvoicing directory.
* ``einvoicing_directory_line``: the directory line used by default for this
  address. The line set on the address itself wins, the line set on the
  customer account is used as a fallback (this is the way Odoo selects the
  directory line of an invoice). It can be set (or removed with a ``null``
  value) from the front end on any address.

``einvoicing_directory_line`` is built from a ``fr.directory.line`` record of
``l10n_fr_einvoicing``: ``id``, ``identifier``, ``type``, ``state`` and
``routing_code_name`` are exposed.

Directory sync  
A service is available to sync the directory of the customer when it encodes
its company identifier (its SIRET) on the site:

``` http
POST /einvoicing/directory_lines
```

``` json
{
  "company_identifier": "73282932000074"
}
```

The company identifier is optional: the service can be called with an empty
payload to refresh the directory with the data already stored on the account.

The service:

* writes the company identifier received on the customer account (it is a
  commercial data, it always belongs to the account). The SIRET must be valid,
  Odoo refuses an invalid one,
* calls ``fr_directory_sync_button()`` on the main partner to query the French
  eInvoicing directory,
* returns the directory lines of the account, including the ``id`` and the
  ``identifier`` of the lines that can be used as default line above.

The directory is always the one of the authenticated customer account (the
main partner), so the service can be called whatever the address the customer
is working on. A ``UserError`` raised by the directory (invalid SIREN, no CTC
session, ...) is returned to the front end as an HTTP 400 error.

Settings  
The countries returned by the ``/settings`` service expose an ``einvoicing``
flag, set when the country code is one of the country codes of France (France
and DOM-TOM, see ``res.company._get_france_country_codes()``).
