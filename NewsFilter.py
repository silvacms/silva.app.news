# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.36 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime

# Silva/News Interfaces
from interfaces import INewsFilter

# Silva/News
from silva.core import conf as silvaconf
from Products.Silva import SilvaPermissions
from NewsItemFilter import NewsItemFilter

class NewsFilter(NewsItemFilter):
    """To enable editors to channel newsitems on a site, all items
        are passed from NewsFolder to NewsViewer through filters. On a filter
        you can choose which NewsFolders you want to channel items for and
        filter the items on several criteria (as well as individually).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News Filter"
    silvaconf.icon("www/news_filter.png")
    silvaconf.priority(3.2)

    implements(INewsFilter)

    _article_meta_types = ['Silva Article Version']
    _agenda_item_meta_types = ['Silva Agenda Item Version']

    def __init__(self, id):
        NewsFilter.inheritedAttribute('__init__')(self, id)
        self._show_agenda_items = 0

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_all_items')
    def get_all_items(self, meta_types=None):
        """
        Returns all items available to this filter. This function will
        probably only be used in the back-end, but nevertheless has
        AccessContentsInformation-security because it does not reveal
        any 'secret' information...
        """
        if not self._sources:
            return []
        query = self._prepare_query(meta_types)
        results = self._query(**query)
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year, meta_types=None):
        """Returns the last self._number_to_show published items
        """
        if not self._sources:
            return []
        month = int(month)
        year = int(year)
        startdate = DateTime(year, month, 1).earliestTime()
        endmonth = month + 1
        if month == 12:
            endmonth = 1
            year = year + 1
        enddate = DateTime(year, endmonth, 1).earliestTime()
        query = self._prepare_query(meta_types)
        query['idx_display_datetime'] = {'query': [startdate, enddate],
                                         'range': 'minmax'}
        result = self._query(**query)

        result = [r for r in result if not r.object_path in
                self._excluded_items]

        return result

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        allowed = self._article_meta_types[:]
        if self.show_agenda_items():
            allowed += self._agenda_item_meta_types[:]
        return allowed

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'show_agenda_items')
    def show_agenda_items(self):
        return self._show_agenda_items

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_show_agenda_items')
    def set_show_agenda_items(self, value):
        self._show_agenda_items = not not int(value)

InitializeClass(NewsFilter)
