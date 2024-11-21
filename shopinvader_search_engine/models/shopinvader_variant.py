# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from sys import exc_info

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = ["shopinvader.variant", "shopinvader.se.binding"]
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"
    _order = "shopinvader_product_id, id"

    def _get_shop_data(self):
        """Use pre-computed index data."""
        return self.get_export_data()

    def _get_binding_to_process(self, bindings, batch_size):
        processing, bindings = super()._get_binding_to_process(bindings, batch_size)
        # We adjust the binding to process by add some extra binding that share
        # the same shopinvader_product_id.
        # This improve perf as
        # most of data are share between variant
        # current update are avoided when generating thumbnail image
        if bindings:
            idx = 0
            while idx < len(bindings) and (
                processing[-1].shopinvader_product_id
                == bindings[idx].shopinvader_product_id
            ):
                idx += 1
            processing, bindings = processing | bindings[0:idx], bindings[idx:]
            if not bindings:
                # if there is no bindings that means that the job has not
                # been splitted. If we are in an exception we just re raise it
                # and the whole list of variants will not be computed.
                # Not doing so would result in an infinite loop unless we
                # force splitting to go down to the exact variant that raises
                # the error, but at the expense of possibly a lot of jobs created
                # raising errors.
                # Note that it can lead to variants not being recomputed which
                # should have been recomputed without error.

                # Note : from python 3.11 on use sys.exception() instead
                e = exc_info()[1]
                if e:
                    raise e

        return processing, bindings
