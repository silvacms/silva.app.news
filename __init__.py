# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.23 $

#python
import os

#Silva
from Products.SilvaExternalSources import ExternalSource

#SilvaNews
import AgendaFilter, NewsFilter, ServiceNews, InlineViewer
import NewsPublication, NewsViewer, AgendaViewer, RSSAggregator
import PlainArticle, PlainAgendaItem
import CategoryFilter
import install

def initialize(context):

    context.registerClass(
        InlineViewer.InlineViewer,
        constructors = (InlineViewer.manage_addInlineViewerForm,
                        InlineViewer.manage_addInlineViewer),
        icon = os.path.join(
                os.path.abspath(
                    os.path.dirname(ExternalSource.__file__)
                ),
                'www/codesource.png')
        )

    context.registerClass(
        ServiceNews.ServiceNews,
        constructors = (ServiceNews.manage_addServiceNewsForm,
                        ServiceNews.manage_addServiceNews),
        icon="www/newsservice.gif"
        )

    from Products.SilvaNews.silvaxml import xmlexport#, xmlimport
    xmlexport.initializeXMLExportRegistry()

import dates
def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('dates',)

# declare a global upgrade registry to use for upgrading SilvaNews
from Products.Silva.upgrade import UpgradeRegistry, GeneralUpgrader
upgrade_registry = UpgradeRegistry()

# import the actual upgraders
import upgrade_13, upgrade_20, upgrade_21, upgrade_26

#register generic upgraders for the major software versions
# where no upgrade is necessary
NothingUpgrader = GeneralUpgrader(upgrade_handler=lambda x: x)
upgrade_registry.registerUpgrader(NothingUpgrader, '2.2', 'Silva Root')
upgrade_registry.registerUpgrader(NothingUpgrader, '2.3', 'Silva Root')
upgrade_registry.registerUpgrader(NothingUpgrader, '2.4', 'Silva Root')
upgrade_registry.registerUpgrader(NothingUpgrader, '2.5', 'Silva Root')

# set the software version, NOTE THAT THIS MUST BE UP-TO-DATE for
# the upgrade to work correctly!!
# use only major and minor version parts, upgrade shouldn't happen
# on patch-level updates
software_version = '2.6'
