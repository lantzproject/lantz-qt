# -*- coding: utf-8 -*-
"""
    lantz.ui.featscan
    ~~~~~~~~~~~~~~~~~

    A Feat Scan frontend and Backend. Builds upon Scan.

    :copyright: 2015 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from ..widgets import WidgetMixin
from ..app import Backend, InstrumentSlot
from .layouts import VerticalUi


class Feat(Backend):
    """A backend to scan a feat for a given instrument."""

    instrument = InstrumentSlot

    #: Name of the scanned feat
    #: :type: str

    def __init__(self, feat_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feat_name = feat_name

    @property
    def feat_units(self):
        """Units of the scanned feat."""
        target = self.instrument
        feat_name = self.feat_name
        feat = target.feats[feat_name]
        return str(feat.units)


class FeatUi(VerticalUi):
    """A Frontend displaying scan parameters with appropriate units."""

    def connect_backend(self):
        target = self.backend.instrument
        feat_name = self.backend.feat_name

        feat = target.feats[feat_name]

        def _pimp(widget):
            WidgetMixin.wrap(widget)
            widget.bind_feat(feat)

        _pimp(getattr(self.widget, self.backend.feat_name))

        super().connect_backend()


