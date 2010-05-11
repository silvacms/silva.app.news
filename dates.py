"""Module that contains formatting code for dates

    includes code to create localized dates
"""

DEFAULT_LOCALE_STRING = 'en'

from AccessControl import ModuleSecurityInfo

import localdatetime
from datetime import datetime
from DateTime import DateTime

module_security = ModuleSecurityInfo('Products.SilvaNews.dates')
__allow_access_to_unprotected_subobjects__ = 1

def _get_fake_self(locale=None):
    class fake_self:
        REQUEST = {'HTTP_ACCEPT_LANGUAGE': locale or DEFAULT_LOCALE_STRING}
    return fake_self()

module_security.declarePublic('DateTimeFormatter')
class DateTimeFormatter:
    """Wrapper for DateTime objects that provides some additional stuff"""

    __allow_access_to_unprotected_subobjects__ = 1

    SHORT = 'short'
    MEDIUM = 'medium'
    LONG = 'long'
    FULL = 'full'

    def __init__(self, dt, locale=None):
        if isinstance(dt, datetime):
            self._datetime = DateTime(dt)
        else:
            self._datetime = dt
        self._locale = locale

    def _get_parts(self):
        return [int(p) for p in self._datetime.parts()[:6]]

    def l_toString(self, format='medium', display_time=True):
        """returns a localized date string of a specified format"""
        if self._datetime is None:
            return ''
        return localdatetime.getFormattedDate(_get_fake_self(self._locale), self._get_parts(), format, display_time=display_time)

def getMonthAbbreviations(locale=None):
    return localdatetime.getMonthAbbreviations(_get_fake_self(locale))
