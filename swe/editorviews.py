from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib import messages
from django.forms.models import modelformset_factory
from swe.context import RequestGlobalContext
#from swe.models import Project
#from swe.editorforms import ProjectForm

def home(request):
    user = request.user
    if not (user.has_perm('swe.can_edit') and user.is_authenticated() and user.is_active):
        return HttpResponseRedirect('/home/')

#    projects=Project.objects.all()
#    ProjectFormSet=modelformset_factory(Project)
#    formset = ProjectFormSet()

#    for form in formset:
#        t = loader.get_template('plainform.html')
#        c = RequestGlobalContext(request,
#                                 {'form': form,
#                                  'action': '/editor/home/'
#                                  })
#        return HttpResponse(t.render(c))


#        if request.method=='POST':
#            form = ProjectForm(request.POST)
#            if form.is_valid():
#                form.save()
#                messages.add_message(request,messages.SUCCESS,'Changes saved')
            #re-render current page
#                t = loader.get_template('plainform.html')
#                c = RequestGlobalContext(request,
#                                         {'form': form,
#                                          'action': '/editor/home/'
#                                          })
#                return HttpResponse(t.render(c))
#            else: 
#                messages.add_message(request,messages.ERROR,'Failed to save changes. Check the form below.')
#                t = loader.get_template('plainform.html')
#                c = RequestGlobalContext(request,
#                                         {'form': form,
#                                          'action': '/editor/home/'
#                                          })
#                return HttpResponse(t.render(c))

            #re-render current page with attached form
#        else:
#            form = ProjectForm(instance=project)
#            t = loader.get_template('todo.html')
#            c = RequestGlobalContext(request,
#                                     {'text': 'no forms',
#                                      })
#            return HttpResponse(t.render(c))
    else:
        t = loader.get_template('todo.html')
        c = RequestGlobalContext(request,
                                 {'text': 'No projects defined.'
                                  })
        return HttpResponse(t.render(c))
