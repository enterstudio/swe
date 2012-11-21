from swe.models import Document
from django.http import HttpResponse
import datetime
from django.template import loader
from swe.context import RequestGlobalContext

def test(request):
    d = Document()
    d.notes = 'doc'
    d.datetime_uploaded = datetime.datetime.today()
    d.save()
    t = loader.get_template('todo.html')
    c = RequestContext(request, {
        'text': "Test.",
    })
    return HttpResponse(t.render(c))


