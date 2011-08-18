# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$

from zope import schema
from zope.i18nmessageid import MessageFactory
from five import grok

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from silva.ui.menu import MenuItem, ContentMenu
from zeam.form import silva as silvaforms
from zeam.form import table as tableforms
from zeam.form.base.datamanager import BaseDataManager


# SilvaNews
from silva.app.news.widgets.path import Path
from silva.app.news.interfaces import INewsFilter
from silva.app.news.filters.NewsItemFilter import NewsItemFilter
from silva.app.news.filters.NewsItemFilter import INewsItemFilterSchema
from silva.app.news import interfaces

_ = MessageFactory('silva_news')


class NewsFilter(NewsItemFilter):
    """To enable editors to channel newsitems on a site, all items
        are passed from NewsFolder to NewsViewer through filters. On a filter
        you can choose which NewsFolders you want to channel items for and
        filter the items on several criteria (as well as individually).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Filter"
    grok.implements(INewsFilter)
    silvaconf.icon("www/news_filter.png")
    silvaconf.priority(3.2)

    _article_meta_types = ['Silva Article']
    _agenda_item_meta_types = ['Silva Agenda Item']

    def __init__(self, id):
        super(NewsFilter, self).__init__(id)
        self._show_agenda_items = 0

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'get_all_items')
    def get_all_items(self, meta_types=None):
        """
        Returns all items available to this filter. This function will
        probably only be used in the back-end.
        """
        if not self.has_sources():
            return []

        query = self._prepare_query(meta_types, public_only=False)
        return self._query_items(query, filter_items=False)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_next_items')
    def get_next_items(self, numdays, meta_types=None):
        if not self.show_agenda_items():
            return []
        return super(NewsFilter, self).get_next_items(
            numdays, meta_types=meta_types)

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        allowed = self._article_meta_types[:]
        if self.show_agenda_items():
            allowed += self._agenda_item_meta_types[:]
        return allowed

    # MANIPULATORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'show_agenda_items')
    def show_agenda_items(self):
        return self._show_agenda_items

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_show_agenda_items')
    def set_show_agenda_items(self, value):
        self._show_agenda_items = not not int(value)


InitializeClass(NewsFilter)


class INewsFilterSchema(INewsItemFilterSchema):
    _show_agenda_items = schema.Bool(
        title=_(u"show agenda items"))


class NewsFilterAddForm(silvaforms.SMIAddForm):
    grok.context(INewsFilter)
    grok.name(u'Silva News Filter')

    fields = silvaforms.Fields(ITitledContent, INewsFilterSchema)


class NewsFilterEditForm(silvaforms.SMIEditForm):
    """ Base form for filters """
    grok.context(INewsFilter)

    fields = silvaforms.Fields(ITitledContent, INewsFilterSchema).omit('id')


class ExcludeAction(silvaforms.Action):

    def __call__(self, form, selected, deselected, unchanged):
        news_filter = form.context
        changed = 0
        for line in selected:
            content = line.getContentData().getContent()
            news_filter.remove_excluded_item(content)
            changed += 1
        for line in deselected:
            content = line.getContentData().getContent()
            news_filter.add_excluded_item(content)
            changed += 1
        if changed:
            form.send_message(
                _(u"Changed exclusion settings for ${count} news item(s).",
                  mapping=dict(count=changed)), type="feedback")
        else:
            form.send_message(
                _(u"No exclusion settings changed."), type="feedback")
        return silvaforms.SUCCESS


class IItemSelection(ITitledContent):
    path = Path(title=_(u'Path'), html_target="_blank")
    display_datetime = schema.Datetime(title=_(u'Display date'))


class ItemSelection(BaseDataManager):

    def __init__(self, content, form):
        self._filter = form.context
        self._get_content_path = form.get_content_path
        self.content = content
        self.version = self.content.get_viewable() or \
            self.content.get_previewable() or \
            self.content.get_editable()

    def get(self, identifier):
        try:
            return getattr(self, identifier)
        except AttributeError:
            raise KeyError(identifier)

    @property
    def select(self):
        return not self._filter.is_excluded_item(self.content)

    @property
    def path(self):
        return self._get_content_path(self.content)

    @property
    def title(self):
        return self.version.get_title_or_id()

    @property
    def display_datetime(self):
        dt = self.version.get_display_datetime()
        if dt is not None:
            return dt.asdatetime()


class Items(silvaforms.SMITableForm):
    grok.baseclass()
    grok.context(interfaces.INewsItemFilter)
    grok.require('silva.ChangeSilvaContent')
    grok.name('items')
    label = _('Items')

    description = _('Uncheck items you want to ignore.')
    ignoreRequest = True
    ignoreContent = False

    mode = silvaforms.DISPLAY
    emptyDescription = _(u"There are no items.")
    tableFields = silvaforms.Fields(IItemSelection).omit('id')
    tableFields['title'].mode = 'silva.icon.edit'
    tableActions = tableforms.TableSelectionActions(
        ExcludeAction(identifier='update', title=_("Update")))

    def createSelectedField(self, item):
        field = super(Items, self).createSelectedField(item)
        field.ignoreContent = False
        field.ignoreRequest = True
        return field


class NewsFilterItems(Items):
    batchSize = 10

    def batchFactory(self, item):
        return ItemSelection(item, self)

    def getItems(self):
        return list(self.context.get_all_items())



class ItemsMenu(MenuItem):
    grok.adapts(ContentMenu, interfaces.INewsItemFilter)
    grok.require('silva.ChangeSilvaContent')
    grok.order(30)
    name = _('Items')
    screen = Items


