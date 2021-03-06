# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8106
import json
import logging

from odoo import _
from odoo.addons.component.core import AbstractComponent, Component
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import locomotivecms
except (ImportError, IOError) as err:
    _logger.debug(err)


_logger = logging.getLogger(__name__)


class LocomotiveAdapter(AbstractComponent):
    _name = "locomotive.abstract.adapter"
    _inherit = ["base.backend.adapter", "base.locomotive.connector"]

    def __init__(self, work_context):
        super(LocomotiveAdapter, self).__init__(work_context)
        backend = self.collection
        self.client = locomotivecms.LocomotiveClient(
            backend.username,
            backend._get_keychain_account()._get_password(),
            backend.handle,
            backend.location,
        )

    def create(self, vals):
        return self.resource.create(vals)

    def write(self, external_id, vals):
        return self.resource.write(external_id, vals)

    def delete(self, binding_id):
        self.resource.delete(binding_id)

    def read(self, external_id):
        return self.resource.read(external_id)

    def search(self, page=1, per_page=80):
        return self.resource.search(page=page, per_page=per_page)


class LocomotiveContentAdapter(Component):
    _name = "locomotive.content.adapter"
    _inherit = "locomotive.abstract.adapter"
    _content_type = None
    _apply_on = []

    def __init__(self, work_context):
        super(LocomotiveContentAdapter, self).__init__(work_context)
        self.resource = self.client.content(self._content_type)


class LocomotiveAssetAdapter(Component):
    _name = "locomotive.asset.adapter"
    _inherit = "locomotive.abstract.adapter"
    _content_type = None
    _apply_on = []

    def __init__(self, work_context):
        super(LocomotiveAssetAdapter, self).__init__(work_context)
        self.resource = self.client.asset()


class LocomotiveBackendAdapter(Component):
    _name = "shopinvader.backend.adapter"
    _inherit = "locomotive.content.adapter"
    _apply_on = "shopinvader.backend"

    def __init__(self, work_context):
        super(LocomotiveBackendAdapter, self).__init__(work_context)
        self.resource = self.client.site()

    def _get_site(self, handle):
        for site in self.resource.search():
            if site["handle"] == handle:
                return site
        raise UserError(_("No site was found for the handle %s") % handle)

    def write(self, handle, vals):
        """
            The write method will only write the "store" information of
            the site in the field "_store" as this field is a custom field
            it's part of the json of the field metafields.
            To update it we need to read it, update it and push it
        """
        site = self._get_site(handle)
        metafields = json.loads(site["metafields"])
        metafields["_store"].update(vals)
        return self.resource.write(
            site["_id"], {"metafields": json.dumps(metafields)}
        )
