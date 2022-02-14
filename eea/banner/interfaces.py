"""Module where all interfaces, events and exceptions live."""
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IEeaBannerLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IBannerSettings(Interface):
    """Client settings for EEA Banner."""

    static_banner_enabled = schema.Bool(
        title="Enable / disable static banner",
        default=True,
        required=False,
    )

    static_banner_visible_to_all = schema.Bool(
        title="Show static banner to anonymous users?",
        default=True,
        required=False,
    )

    static_banner_type = schema.Choice(
        title="Static banner type",
        default="warning",
        vocabulary=SimpleVocabulary.fromValues(
            ["success", "warning", "error"]
        ),
    )

    static_banner_title = schema.TextLine(
        title="Static banner title",
        default="This is a demo/test instance",
        required=False,
    )

    static_banner_message = schema.Text(
        title="Static banner message",
        required=False,
        default=(
            "Do not use it for operational purposes. "
            "All changes will be regularly overwritten"
        ),
    )

    dynamic_banner_enabled = schema.Bool(
        title="Enable / disable dynamic banner",
        default=True,
        required=False,
        description=(
            "It will appear only if status of at least one stack "
            "is not 'active'"
        ),
    )

    dynamic_banner_visible_to_all = schema.Bool(
        title="Show dynamic banner to anonymous users?",
        default=True,
        required=False,
    )

    rancher_stacks = schema.List(
        title="Rancher stacks to monitor",
        required=False,
        default=[],
        value_type=schema.TextLine(),
    )

    dynamic_banner_title = schema.TextLine(
        title="Dynamic banner title",
        default="Web admins says:",
        required=False,
    )

    dynamic_banner_message = schema.Text(
        title="Dynamic banner message",
        required=False,
        default="The system is {}",
        description=(
            "Add suffix/prefix to rancher stacks status message. "
            "Use {} for rancher stacks status placeholder"
        ),
    )
