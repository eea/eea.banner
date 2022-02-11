"""RestAPI enpoint @banner GET"""
import requests
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from eea.cache import cache
from eea.banner.interfaces import IBannerSettings

TIMEOUT = 15
RANCHER_METADATA = "http://rancher-metadata/latest"
MEMCACHE_AGE = 300


@implementer(IPublishTraverse)
class BannerGet(Service):
    """Banner GET"""

    def get_rancher_metadata(self, url):
        """Returns Rancher metadata API"""
        try:
            req = requests.get(
                url, headers={"Accept": "application/json"}, timeout=TIMEOUT
            )
            result = req.json()
        except Exception:
            result = []
        return result

    def get_stacks(self):
        """Returns all Rancher stacks from the current environment"""
        url = "%s/stacks" % RANCHER_METADATA
        return self.get_rancher_metadata(url)

    @cache(lambda *args: "rancher-status", lifetime=MEMCACHE_AGE)
    def get_stacks_status(self, stacks):
        """Returns status of required stacks"""
        status = None
        rancher_stacks = self.get_stacks()
        for stack in rancher_stacks:
            if stack.get("system") or stack.get("name") not in stacks:
                continue
            if not status and stack.get("state") != "active":
                status = stack.get("state")
                break
        return status

    def reply(self):
        """Reply"""
        development = self.request.form.get("development")
        return {
            "active": api.portal.get_registry_record(
                "active", interface=IBannerSettings, default=""
            ),
            "visible_to_all": api.portal.get_registry_record(
                "visible_to_all", interface=IBannerSettings, default=""
            ),
            "visible_on_login": api.portal.get_registry_record(
                "visible_on_login", interface=IBannerSettings, default=""
            ),
            "type": api.portal.get_registry_record(
                "type", interface=IBannerSettings, default=""
            ),
            "title": api.portal.get_registry_record(
                "title", interface=IBannerSettings, default=""
            ),
            "message": api.portal.get_registry_record(
                "message", interface=IBannerSettings, default=""
            ),
            "stacks_status": None
            if development
            else self.get_stacks_status(
                api.portal.get_registry_record(
                    "stacks", interface=IBannerSettings, default=""
                )
            ),
            "stacks_status_message_template": api.portal.get_registry_record(
                "stacks_status_message_template",
                interface=IBannerSettings,
                default="",
            ),
        }
