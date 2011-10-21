# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

# Zope
from DateTime import DateTime
from datetime import datetime

# Silva
from silva.core.conf.interfaces import ITitledContent
from silva.core.smi.content import ContentEditMenu
from silva.core.smi.content.publish import IPublicationFields
from silva.core.smi.content.publish import Publish
from silva.core.views import views as silvaviews
from silva.ui.menu import MenuItem
from zeam.form import silva as silvaforms
from zeam.form import autofields

from silva.app.news.interfaces import INewsItem
from silva.app.news.NewsCategorization import INewsCategorizationSchema


_ = MessageFactory('silva_news')


class INewsItemSchema(ITitledContent, INewsCategorizationSchema):
    external_url = schema.URI(
        title=_(u"External URL"),
        description=_(u"external URL with more information "
                      u"about this news item."),
        required=False)


class NewsItemAddForm(silvaforms.SMIAddForm):
    grok.context(INewsItem)
    grok.name(u"Silva Article")

    fields = silvaforms.Fields(INewsItemSchema)


class NewsItemDetailsForm(silvaforms.SMIEditForm):
    grok.context(INewsItem)
    grok.name('details')

    label = _(u"Article details")
    fields = silvaforms.Fields(INewsItemSchema).omit('id')


class NewsItemDetailsMenu(MenuItem):
    grok.adapts(ContentEditMenu, INewsItem)
    grok.require('silva.ChangeSilvaContent')
    grok.order(15)

    name = _('Details')
    screen = NewsItemDetailsForm


class NewsItemPublicationPortlet(silvaviews.Viewlet):
    grok.context(INewsItem)
    grok.view(Publish)
    grok.viewletmanager(silvaforms.SMIFormPortlets)
    grok.order(20)

    def update(self):
        viewable = self.context.get_viewable()
        self.display_date = None
        if viewable is not None:
            format = self.request.locale.dates.getFormatter('dateTime').format
            convert = lambda d: d is not None and format(d.asdatetime()) or None
            self.display_date = convert(viewable.get_display_datetime())


# Add display datetime on publish smi tab

class INewsItemPublicationFields(Interface):
    display_datetime = schema.Datetime(title=_("Display datetime"))


class NewsItemPublication(grok.Adapter):
    grok.context(INewsItem)
    grok.provides(INewsItemPublicationFields)

    @apply
    def display_datetime():

        def getter(self):
            current = self.context.get_unapproved_version_display_datetime()
            if current is None:
                return datetime.now()
            return current

        def setter(self, value):
            self.context.set_unapproved_version_display_datetime(
                DateTime(value))

        return property(getter, setter)


class NewsItemPublicationFields(autofields.AutoFields):
    autofields.context(INewsItem)
    autofields.group(IPublicationFields)
    autofields.order(20)
    fields = silvaforms.Fields(INewsItemPublicationFields)


