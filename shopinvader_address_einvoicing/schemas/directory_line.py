# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import typing

from extendable_pydantic import StrictExtendableBaseModel

DirectoryLineType = typing.Literal["siren", "siret", "routing_code", "suffix", "error"]
DirectoryLineState = typing.Literal["upcoming", "active", "disabled", "inactive"]


class DirectoryLine(StrictExtendableBaseModel):
    """Line of the French eInvoicing directory of a partner."""

    id: int
    identifier: str
    type: DirectoryLineType | None = None
    state: DirectoryLineState | None = None
    routing_code_name: str | None = None

    @classmethod
    def from_fr_directory_line(cls, odoo_rec):
        """Build the schema from a ``fr.directory.line`` record.

        ``None`` is returned when the partner has no directory line selected:
        the field is then exposed as ``null``.
        """
        if not odoo_rec:
            return None
        return cls.model_construct(
            id=odoo_rec.id,
            identifier=odoo_rec.identifier,
            type=odoo_rec.type or None,
            state=odoo_rec.state or None,
            routing_code_name=odoo_rec.routing_code_name or None,
        )


class DirectoryLineSyncInput(StrictExtendableBaseModel, extra="ignore"):
    """Payload used to sync the directory of the customer.

    The vat is written on the account before the sync since the directory is
    queried with the data stored on the account.
    """

    vat: str | None = None
