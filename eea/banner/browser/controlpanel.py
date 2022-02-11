from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from eea.banner.interfaces import IBannerSettings


class BannerRegistryEditForm(RegistryEditForm):
    schema = IBannerSettings
    id = "banner"
    label = "Banner Settings"


class BannerControlPanelFormWrapper(ControlPanelFormWrapper):
    form = BannerRegistryEditForm
