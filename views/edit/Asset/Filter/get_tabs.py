## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# define name, id, up_id
# define:
# name, id, up_id, toplink_accesskey, tab_accesskey, uplink_accesskey
tabs = [('editor', 'tab_edit', 'tab_edit', '!', '1', '6'),
        ('items', 'tab_edit_items', 'tab_edit', '@', '2', '7'),
        ('properties', 'tab_metadata', 'tab_metadata', '#', '3', '8'),
        ('access', 'tab_access', 'tab_access', '$', '4', '9'),
       ]
return tabs