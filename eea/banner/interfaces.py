"""Module where all interfaces, events and exceptions live."""
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IEeaBannerLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IBannerSettings(Interface):
    """Client settings for EEA Banner."""

    active = schema.Bool(
        title="Active",
        default=True,
        required=False,
    )

    visible_to_all = schema.Bool(
        title="Show to anonymous users?",
        default=True,
        required=False,
    )

    visible_on_login = schema.Bool(
        title="Show on login form?",
        default=True,
        required=False,
    )

    type = schema.Choice(
        title="Type",
        default="warning",
        vocabulary=SimpleVocabulary.fromValues(
            ["success", "warning", "error"]
        ),
    )

    title = schema.TextLine(
        title="Title",
        default="This is a demo/test instance",
        required=False,
    )

    message = schema.List(
        title="Message",
        required=False,
        default=[
            """Do not use it for operational purposes.
            All changes will be regularly overwritten"""
        ],
        value_type=schema.TextLine(),
    )

    stacks = schema.List(
        title="Rancher stacks",
        description="List of rancher stacks for status checking",
        required=False,
        default=[],
        value_type=schema.TextLine(),
    )

    stacks_status_message_template = schema.TextLine(
        title="Stacks status message template",
        description="""Add suffix/prefix to stacks status message.
        Use {} for status placeholder""",
        default="Web admins says: the system is {}",
        required=False,
    )
