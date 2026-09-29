Addresses  \nEvery address (invoicing or delivery) exposed by the address services
exposes the eInvoicing directory of the customer account:

* ``default_fr_directory_line_id``: the directory line used by default for
  this address. The line set on the address itself wins, the line set on the
  customer account is used as a fallback (this is the way Odoo selects the
  directory line of an invoice). It can be set (or removed with a ``null``
  value) from the front end on any address.
* ``fr_directory_line_ids``: the directory lines of the customer account.
  They are the lines that can be selected as default line: the lines disabled
  in the directory are not exposed.

Both fields are built from ``fr.directory.line`` records of
``l10n_fr_einvoicing``.

Directory sync  \nA service is available to sync the directory of the customer when it encodes
its vat number on the site:

``` http
POST /einvoicing/directory_lines
```

``` json
{
  "vat": "FR44732829320"
}
```

The vat is optional: the service can be called with an empty payload to
refresh the directory with the data already stored on the account.

The service:

* writes the vat received on the customer account (the vat is a commercial
  field, it always belongs to the account),
* calls ``fr_directory_sync_button()`` on the main partner to query the
  French eInvoicing directory,
* returns the directory lines of the account, in the same format as the
  ``fr_directory_line_ids`` field of the addresses.

The directory is always the one of the authenticated customer account (the
main partner), so the service can be called whatever the address the customer
is working on. A ``UserError`` raised by the directory (invalid SIREN, no CTC
session, ...) is returned to the front end as an HTTP 400 error.

Settings  \nThe countries returned by the ``/settings`` service expose an ``einvoicing``
flag, set when the country code is one of the country codes of France (France
and DOM-TOM, see ``res.company._get_france_country_codes()``).
