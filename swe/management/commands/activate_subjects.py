import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import utc
from swe.models import Subject, SubjectCategory, SubjectList
from swe.datafiles.subjectdata import SubjectData

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):

        for active_subjectlist in SubjectList.objects.filter(is_active=True):
            active_subjectlist.is_active = False
            active_subjectlist.save()
        
        new_subjectlist = SubjectList(
            is_active=True,
            date_activated=datetime.datetime.utcnow().replace(tzinfo=utc),
            )
        new_subjectlist.save()

        subjects = SubjectData.subjects
        order_counter1 = 0
        for category in subjects:
            #category = ('category_name', [('subject_name',is_active), ...]
            c = SubjectCategory(
                subjectlist=new_subjectlist,
                display_text=category[0],
                display_order=order_counter1,
                )
            order_counter1 += 1
            c.save()
                            
            order_counter2 = 0
            for subject in category[1]:
                s = Subject(
                    subjectcategory=c,
                    display_text=subject[0],
                    is_enabled=subject[1],
                    display_order=order_counter2,
                    )
                order_counter2 += 1
                s.save()
