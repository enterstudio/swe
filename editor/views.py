from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from swe.context import RequestGlobalContext

def home(request):
    t = loader.get_template('todo.html')
    c = RequestGlobalContext(
        request,{
            'text': "Editor home",
    })
    return HttpResponse(t.render(c))

