# Create groups

import os
currentdir = os.path.dirname(os.path.abspath(__file__))
rootdir = os.path.join(currentdir,'..')
os.sys.path.insert(0,rootdir) 

import settings
from django.core.management  import setup_environ     #environment setup function

setup_environ(settings)

from django.contrib.auth.models import Group, Permission

editors = Group(name='Editors')
editors.save()
managers = Group(name='Managers')
managers.save()

#-------------------------------------

# Create permissions
# Run this in python manage.py shell

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get(app_label='swe', model='Project')
edit_permission = Permission.objects.create(codename='can_edit',
                                       name='Can Edit a Manuscript',
                                       content_type=content_type)

edit_permission.save()

approve_permission = Permission.objects.create(codename='can_approve',
                                       name='Can Approve an Edited Manuscript',
                                       content_type=content_type)

approve_permission.save()


edit_permission = Permission.objects.filter(codename='can_edit')[0]
editors = Group.objects.filter(name="Editors")[0]
editors.permissions.add(edit_permission)

approve_permission = Permission.objects.filter(codename='can_approve')[0]
managers = Group.objects.filter(name="Managers")[0]
managers.permissions.add(approve_permission)
managers.permissions.add(edit_permission)

#--------------------------------------------

# Add a specific user to a group

#managers = Group.objects.get(name='Managers')
#user = User.objects.get(email='ntdmn@hotmail.com')
#user.groups.add(managers)
#user.save()
