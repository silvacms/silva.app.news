# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.5 $
# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
# Silva
from Products.Silva.Publication import Publication
from Products.Silva.IPublication import IPublication
from Products.Silva import SilvaPermissions
#misc
from Products.Silva.helpers import add_and_edit
from Products.SilvaNews.INewsItem import INewsItem

class NewsSource(Publication, CatalogPathAware):
    """Source
    """
    security = ClassSecurityInfo()

    meta_type = "Silva NewsSource"

    __implements__ = IPublication

    default_catalog = 'service_catalog'

    def __init__(self, id, title):
        NewsSource.inheritedAttribute('__init__')(self, id, title)
        self._is_private = 0

    def manage_afterAdd(self, item, container):
        NewsSource.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.index_object()

    def manage_beforeDelete(self, item, container):
        NewsSource.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.unindex_object()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'object_title')
    def object_title(self):
        return self._title

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_private')
    def is_private(self):
        """Returns the private-state
        """
        return self._is_private

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'source_path')
    def parent_path(self):
        """Returns the path of the parent of this source
        """
        return '/'.join(self.aq_inner.aq_parent.getPhysicalPath())

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_private')
    def set_private(self, on_or_off):
        """Sets the is_private-setting for this source, is_private can restrict the
        availability of this source towards the outside-world (when set, the source
        can only be found by filters in the same subdirectory)
        """
        self._is_private = on_or_off
        self.reindex_object()
        self._p_changed = 1
        self.reindex_object()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_fields_for_bulk_editing')
    def get_fields_for_bulk_editing(self, field_keys, objectids, startpoint=None):
        """Creates a dictionary of values for each field in field_keys, if the value is None
        the field should not be shown (the objects do not have the field available at all),
        if it is a string containing '__DO_NOT_FILL_FIELD__', the field should be created but
        not filled (some of the objects have the field, but the value is different for them)
        and if the value is something else, the field should be filled (some of the objects
        contain the field, and the value is the same for all of them (which is the value of the
        dictionary-item"""
        if startpoint is None:
            startpoint = self
        versionpaths = []
        fields = {}
        for key in field_keys:
            fields[key] = None

        # walk through the objects, they should be in direct children of this object
        for item in objectids:
            currentobj = getattr(startpoint, item)
            if INewsItem.isImplementedBy(currentobj):
                version = currentobj.get_editable()
                versionpaths.append(currentobj.getPhysicalPath())
                if not version:
                    # no editable version
                    continue
                for key in fields.keys():
                    if hasattr(version, key):
                        value = getattr(version, key)()
                        if fields[key] is None:
                            fields[key] = value
                        elif fields[key] != value:
                            fields[key] = '__DO_NOT_FILL_FIELD__'
            elif currentobj.implements_container() or currentobj.implements_publication():
                # this is a folder, so walk through it...
                morefields, morepaths = self.get_fields_for_bulk_editing(field_keys, currentobj.objectIds(), currentobj)
                versionpaths += morepaths
                for key in morefields.keys():
                    if fields[key] != morefields[key]:
                        if morefields[key] == '__DO_NOT_FILL_FIELD__':
                            fields[key] = '__DO_NOT_FILL_FIELD__'
                        elif morefields[key] is not None and fields[key] is None:
                            fields[key] = morefields[key]
                        elif morefields[key] is not None and fields[key] is not None:
                            fields[key] = '__DO_NOT_FILL_FIELD__'
        return (fields, versionpaths)

    security.declareProtected(SilvaPermissions.AccessContentsInformation, 'get_silva_addables')
    def get_silva_addables(self):
        result = [addable_dict
                for addable_dict in self.filtered_meta_types()
                if self._is_silva_addable(addable_dict)]
        result.sort(lambda x, y: cmp(x['name'], y['name']))
        return result

    def _is_silva_addable(self, addable_dict):
        """Given a dictionary from filtered_meta_types, check whether this
        specifies a NewsItem. This method is overridden from Folder to control the
        meta-types addable in the newssources
        """
        return (
            addable_dict.has_key('instance') and
            INewsItem.isImplementedByInstancesOf(
            addable_dict['instance']))

InitializeClass(NewsSource)

manage_addNewsSourceForm = PageTemplateFile("www/newsSourceAdd", globals(),
                                             __name__='manage_addNewsSourceForm')

def manage_addNewsSource(self, id, title, create_default=1, REQUEST=None):
    """Add a Silva Newssource."""
    if not self.is_id_valid(id):
        return
    object = NewsSource(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
