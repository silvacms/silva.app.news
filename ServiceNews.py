# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.15 $

from zope.interface import implements

import Globals
from AccessControl import ClassSecurityInfo
from OFS.interfaces import IObjectWillBeRemovedEvent
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Silva
from silva.core import conf as silvaconf
from Products.Silva.BaseService import SilvaService
from Products.Silva.helpers import add_and_edit, \
     register_service, unregister_service

#SilvaNews
import Tree
from dates import DateTimeFormatter, getMonthAbbreviations
from interfaces import IServiceNews
from Products.SilvaNews import software_version


class CategoryMixin(object):
    """Code that can be shared between category users for the
    purpose of generating flat lists of SilvaNews categories"""
    """Currently used by NewsService and CategoryFilter"""

    security = ClassSecurityInfo()
    silvaconf.baseclass()

    security.declareProtected('View', 'subject_tree')
    def subject_tree(self,audject=None):
        """returns a list (id, title, depth) for all elements in the tree"""
        ret = []
        self._flatten_tree_helper(self._subjects, ret, filterby=audject)
        return ret

    security.declareProtected('View', 'subject_form_tree')
    def subject_form_tree(self, audject=None):
        """returns a list (html_repr, id) for each element

            html_repr consists of '%s%s' % (
                (depth * 2 * '&nsbp;'), title)
        """
        tree = self.subject_tree(audject)
        return self._form_tree_helper(tree)

    security.declareProtected('View', 'target_audience_tree')
    def target_audience_tree(self,audject=None):
        """returns a list (id, title, depth) for all elements in the tree"""
        ret = []
        self._flatten_tree_helper(self._target_audiences, ret, filterby=audject)
        return ret

    security.declareProtected('View', 'target_audience_form_tree')
    def target_audience_form_tree(self, audject=None):
        """see subject_form_tree"""
        tree = self.target_audience_tree(audject)
        return self._form_tree_helper(tree)
        
    def _form_tree_helper(self, tree):
        ret = []
        for el in tree:
            r = '%s%s' % ((el[2] * 2 * '&nbsp;'), el[1])
            ret.append((r, el[0]))
        return ret

    def _flatten_tree_helper(self, tree, ret, depth=0, filterby=[]):
        els = tree.children()
        els.sort(lambda a, b: cmp(a.id(), b.id()))
        for el in els:
            if not filterby or el.id() in filterby:
                ret.append((el.id(), el.title(), depth))
            self._flatten_tree_helper(el, ret, depth+1, filterby=filterby)
Globals.InitializeClass(CategoryMixin)
    
class ServiceNews(SilvaService, CategoryMixin):
    """This object provides lists of subjects and target_audiences for Filters
    """
    implements(IServiceNews)
    security = ClassSecurityInfo()
    meta_type = 'Silva News Service'

    silvaconf.icon('www/newsservice.gif')
    silvaconf.factory('manage_addServiceNews')

    manage_options = (
                      {'label': 'Edit', 'action': 'manage_main'},
   #                   {'label': 'Info', 'action': 'manage_info_tab'}
                      ) + SimpleItem.manage_options

    manage_main = edit_tab = PageTemplateFile('www/serviceNewsEditTab',
                                            globals(), 
                                            __name__='edit_tab')
    manage_rename_view = PageTemplateFile('www/serviceNewsRenameView',
                                            globals(), 
                                            __name__='manage_rename_view')
    manage_info_tab = PageTemplateFile('www/serviceNewsInfoTab',
                                            globals(), 
                                            __name__='manage_info_tab')

    def __init__(self, id, title):
        SilvaService.__init__(self, id, title)
        self._subjects = Tree.Root()
        self._target_audiences = Tree.Root()
        self._locale = 'en'
        self._date_format = 'medium'
        self._content_version = software_version
		
        self.add_subject(u'generic',u'Generic')
        self.add_target_audience(u'all',u'All')

    security.declareProtected('Setup ServiceNews',
                                'add_subject')
    def add_subject(self, id, title, parent=None):
        """add a subject to the tree"""
        node = Tree.Node(id, title)
        parentnode = self._subjects
        if parent is not None:
            parentnode = self._subjects.getElement(parent)
        parentnode.addChild(node)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                                'add_target_audience')
    def add_target_audience(self, id, title, parent=None):
        """add a target audience to the tree"""
        node = Tree.Node(id, title)
        parentnode = self._target_audiences
        if parent is not None:
            parentnode = self._target_audiences.getElement(parent)
        parentnode.addChild(node)
        self._p_changed = 1

    security.declareProtected('View',
                                'subjects')
    def subjects(self):
        """returns a list of (id, title) tuples"""
        return [(x.id(), x.title()) for x in  self._subjects.getElements()]

    security.declareProtected('View',
                                'subject_title')
    def subject_title(self, id):
        """returns the title of a certain subject"""
        try:
            el = self._subjects.getElement(id)
        except KeyError:
            return None
        return el.title()

    def filtered_subject_form_tree(self, context):
        """ tries to acquire the nearest news category filter
        in the content, and returns a subject_form_tree with the
        subjects selected in the filter removed.
        This method is primarliy used in the add screens of
        SNN objects"""
        audject = context.superValues('Silva News Category Filter')
        if audject:
            audject = audject[0].subjects()
        return self.subject_form_tree(audject)

    def filtered_ta_form_tree(self, context):
        """ tries to acquire the nearest news category filter
        in the content, and returns a ta_form_tree with the
        ta's selected in the filter removed.
        This method is primarliy used in the add screens of
        SNN objects"""
        audject = context.superValues('Silva News Category Filter')
        if audject:
            audject = audject[0].target_audiences()
        return self.target_audience_form_tree(audject)

    security.declareProtected('View',
                                'target_audiences')
    def target_audiences(self):
        """returns a list of (id, title) tuples"""
        return [(x.id(), x.title()) for x in 
                self._target_audiences.getElements()]

    security.declareProtected('View',
                                'target_audience_title')
    def target_audience_title(self, id):
        """returns the title of a certain target audience"""
        try:
            el = self._target_audiences.getElement(id)
        except KeyError:
            return None
        return self._target_audiences.getElement(id).title()

    security.declareProtected('Setup ServiceNews',
                                'remove_subject')
    def remove_subject(self, id):
        """removes a subject by id"""
        node = self._subjects.getElement(id)
        if node.children():
            raise ValueError, 'node not empty'
        node.parent().removeChild(node)
        self._p_changed = 1

    security.declareProtected('Setup ServiceNews',
                                'remove_target_audience')
    def remove_target_audience(self, id):
        """removes a target audience by id"""
        node = self._target_audiences.getElement(id)
        if node.children():
            raise ValueError, 'node not empty'
        node.parent().removeChild(node)
        self._p_changed = 1

            
    security.declareProtected('View',
                                'locale')
    def locale(self):
        """returns the current locale (used to format public dates)"""
        return self._locale

    security.declareProtected('View',
                                'date_format')
    def date_format(self):
        """returns the current date format

            Z3's locale package has a nunber of different date formats to 
            choose from per locale, managers can set what format to use
            on this service (since there's no better place atm)
        """
        return self._date_format

    security.declareProtected('Setup ServiceNews',
                              'manage_add_subject')
    def manage_add_subject(self, REQUEST):
        """Add a subject"""
        if (not REQUEST.has_key('subject') or not 
                REQUEST.has_key('parent') or REQUEST['subject'] == ''
                or not REQUEST.has_key('title') or REQUEST['title'] == ''):
            return self.edit_tab(
                        manage_tabs_message='Missing id or title')

        if REQUEST['parent']:
            try:
                self.add_subject(unicode(REQUEST['subject'], 'UTF-8'), 
                                    unicode(REQUEST['title'], 'UTF-8'),
                                    unicode(REQUEST['parent'], 'UTF-8'))
            except Tree.DuplicateIdError, e:
                return self.edit_tab(manage_tabs_message=e)
        else:
            try:
                self.add_subject(unicode(REQUEST['subject'], 'UTF-8'),
                                    unicode(REQUEST['title'], 'UTF-8'))
            except Tree.DuplicateIdError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(
                    manage_tabs_message='Subject %s added' % 
                        unicode(REQUEST['subject'], 'UTF-8'))

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_subject')
    def manage_remove_subject(self, REQUEST):
        """Remove a subject"""
        if not REQUEST.has_key('subjects'):
            return self.edit_tab(manage_tabs_message='No subjects specified')

        subs = [unicode(s, 'UTF-8') for s in REQUEST['subjects']]
        for subject in subs:
            try:
                self.remove_subject(subject)
            except (KeyError, ValueError), e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(
                manage_tabs_message='Subjects %s removed' % ', '.join(subs))
        
    security.declareProtected('Setup ServiceNews',
                              'manage_add_target_audience')
    def manage_add_target_audience(self, REQUEST):
        """Add a target_audience"""
        if (not REQUEST.has_key('target_audience') or
                not REQUEST.has_key('parent') or 
                REQUEST['target_audience'] == '' or
                not REQUEST.has_key('title') or 
                REQUEST['title'] == ''):
            return self.edit_tab(
                manage_tabs_message='Missing id or title')

        if REQUEST['parent']:
            try:
                self.add_target_audience(
                            unicode(REQUEST['target_audience'], 'UTF-8'), 
                            unicode(REQUEST['title'], 'UTF-8'),
                            unicode(REQUEST['parent'], 'UTF-8'))
            except Tree.DuplicateIdError, e:
                return self.edit_tab(manage_tabs_message=e)
        else:
            try:
                self.add_target_audience(
                            unicode(REQUEST['target_audience'], 'UTF-8'),
                            unicode(REQUEST['title'], 'UTF-8'))
            except Tree.DuplicateIdError, e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(
                    manage_tabs_message='Target audience %s added' % 
                        unicode(REQUEST['target_audience'], 'UTF-8'))

    security.declareProtected('Setup ServiceNews',
                              'manage_remove_target_audience')
    def manage_remove_target_audience(self, REQUEST):
        """Remove a target_audience"""
        if not REQUEST.has_key('target_audiences'):
            return self.edit_tab(
                    manage_tabs_message='No target audience specified')

        tas = [unicode(t, 'UTF-8') for t in REQUEST['target_audiences']]
        for target_audience in tas:
            try:
                self.remove_target_audience(target_audience)
            except (KeyError, ValueError), e:
                return self.edit_tab(manage_tabs_message=e)

        return self.edit_tab(
                    manage_tabs_message='Target audiences %s removed' % 
                        ', '.join(tas))

    security.declareProtected('Setup ServiceNews',
                              'manage_rename_start')
    def manage_rename_start(self, REQUEST):
        """Rename one or more items"""
        if (not REQUEST.has_key('subjects') and not 
                REQUEST.has_key('target_audiences')):
            return self.edit_tab(
                manage_tabs_message='No items selected to rename')
        return self.manage_rename_view()

    security.declareProtected('Setup ServiceNews', 
                              'manage_rename_subjects')
    def manage_rename_subjects(self, REQUEST):
        """Rename subjects"""
        illegal = []
        for name, value in REQUEST.form.items():
            if name.startswith('title_'):
                continue
            uname = unicode(name, 'UTF-8')
            uvalue = unicode(value, 'UTF-8')
            subject = self._subjects.getElement(uname)
            if uvalue != subject.id():
                try:
                    subject.set_id(uvalue)
                except Tree.DuplicateIdError:
                    illegal.append(uvalue)
                    continue
            title = unicode(REQUEST.form['title_%s' % name], 'UTF-8')
            subject.set_title(title)
            self._p_changed = 1
        if illegal:
            return self.edit_tab(
                manage_tabs_message=
                    'Items %s could not be renamed (name already in use).' % 
                        ', '.join(illegal))
        else:
            return self.edit_tab(manage_tabs_message='Items renamed')

    security.declareProtected('Setup ServiceNews', 
                              'manage_rename_target_audiences')
    def manage_rename_target_audiences(self, REQUEST):
        """Rename target audiences"""
        illegal = []
        for name, value in REQUEST.form.items():
            if name.startswith('title_'):
                continue
            uname = unicode(name, 'UTF-8')
            uvalue = unicode(value, 'UTF-8')
            audience = self._target_audiences.getElement(uname)
            if uvalue != audience.id():
                try:
                    audience.set_id(uvalue)
                except Tree.DuplicateIdError:
                    illegal.append(uvalue)
                    continue
            title = unicode(REQUEST.form['title_%s' % name], 'UTF-8')
            audience.set_title(title)
            self._p_changed = 1
        if illegal:
            return self.edit_tab(
                manage_tabs_message=
                    'Items %s could not be renamed (name already in use).' % 
                        ', '.join(illegal))
        else:
            return self.edit_tab(manage_tabs_message='Items renamed')

    # XXX we probably want to move these elsewhere, for now however this seems
    # the most logical location
    security.declareProtected('Setup ServiceNews',
                                'manage_set_locale')
    def manage_set_locale(self, REQUEST):
        """set the locale and date format
            
            used for displaying public date/times
        """
        if not REQUEST.has_key('locale'):
            return self.edit_tab(
                manage_tabs_message="No locale provided!")
        if not REQUEST.has_key('date_format'):
            return self.edit_tab(
                manage_tabs_message="No date format provided!")
        self._locale = REQUEST['locale']
        self._date_format = REQUEST['date_format']

    security.declareProtected('View',
                                'format_date')
    def format_date(self, datetime, display_time=True):
        """returns a formatted datetime string
           takes the service's locale setting into account
        """
        if not datetime:
            return ''
        formatter = DateTimeFormatter(datetime, self._locale)
        return formatter.l_toString(self._date_format, 
                                    display_time=display_time)

    security.declareProtected('View',
                                'get_month_abbrs')
    def get_month_abbrs(self):
        """returns a list of localized abbreviated month names"""
        return getMonthAbbreviations(self._locale)
       
    security.declareProtected('Setup ServiceNews',
                                'upgrade')
    def upgrade(self):
        """upgrade the Silva instance's news elements"""
        from Products.SilvaNews import upgrade_registry
        content_version = self.content_version()
        software_version = self.software_version()
        if content_version == software_version:
            return
        root = self.get_root()
        upgrade_registry.upgrade(root, content_version, software_version)
        
        root.service_news._content_version = software_version

        return self.edit_tab(manage_tabs_message='Upgrade succeeded')

    security.declareProtected('Setup ServiceNews',
                                'upgrade_required')
    def upgrade_required(self):
        """returns True if an upgrade is necessary"""
        return not (self.content_version() == self.software_version())

    security.declareProtected('Setup ServiceNews',
                                'software_version')
    def software_version(self):
        return software_version

    security.declareProtected('Setup ServiceNews',
                                'content_version')
    def content_version(self):
        # defaults to 1.2 since the attr is set on 1.3
        return getattr(self, '_content_version', '1.2')

Globals.InitializeClass(ServiceNews)

def manage_addServiceNews(self, id, title='', REQUEST=None):
    """Add service to folder
    """
    # add actual object
    service = ServiceNews(id, title)
    register_service(self, id, service, IServiceNews)
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''

@silvaconf.subscribe(IServiceNews, IObjectWillBeRemovedEvent)
def unregisterNewsService(service, event):
    unregister_service(service, IServiceNews)