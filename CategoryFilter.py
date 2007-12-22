from zope.interface import implements

# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

# Silva/News Interfaces
from interfaces import ICategoryFilter

# Silva/News
from Products.Silva import SilvaPermissions
from Products.Silva.i18n import translate as _
from Products.SilvaNews.Filter import Filter

class CategoryFilter(Filter):
    """A CategoryFilter that is editable in silva.  It allows you to specify elements in the silva news article and silva news filter to hide from content authors"""

    security = ClassSecurityInfo()

    meta_type = "Silva News Category Filter"

    implements(ICategoryFilter)

    def __init__(self, id):
        Filter.__init__(self, id)

#I think this stuff below should be integrated somewhere to get the lists of subjects and audiences to indent like they do on service_news
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'subject_form_tree')
    def subject_form_tree(self):
        """returns a list (html_repr, id) for each element

            html_repr consists of '%s%s' % (
                (depth * 2 * '&nsbp;'), title)
        """
        tree = self.subject_tree()
        return self._form_tree_helper(tree)

    def _form_tree_helper(self, tree):
        ret = []
        for el in tree:
            r = '%s%s' % ((el[2] * 2 * '&nbsp;'), el[1])
            ret.append((r, el[0]))
        return ret

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'subject_tree')
    def subject_tree(self):
        """returns a list (id, title, depth) for all elements in the tree"""
        ret = []
        self._flatten_tree_helper(self._subjects, ret)
        return ret

    def _flatten_tree_helper(self, tree, ret, depth=0):
        els = tree.children()
        els.sort(lambda a, b: cmp(a.id(), b.id()))
        for el in els:
            ret.append((el.id(), el.title(), depth))
            self._flatten_tree_helper(el, ret, depth+1)
#I think this stuff above should be integrated somewhere to get the lists of subjects and audiences to indent like they do on service_news

InitializeClass(CategoryFilter)