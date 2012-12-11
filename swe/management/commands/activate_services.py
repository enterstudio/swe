import datetime
from django.utils.timezone import utc
from django.core.management.base import BaseCommand
from django.db import transaction
from swe.datafiles.servicedata import ServiceData
from swe.models import ServiceList, ServiceType, WordCountRange, PricePoint


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        
        activeservicelists = ServiceList.objects.filter(is_active=True)
        for activeservicelist in activeservicelists:
            activeservicelist.is_active = False
            activeservicelist.save()
            
        new_servicelist = ServiceList(
            is_active=True,
            date_activated=datetime.datetime.utcnow().replace(tzinfo=utc),
            )
        new_servicelist.save()

        servicetypes_new = []
        for servicetype in ServiceData.servicetypes:
            s = ServiceType(
                servicelist=new_servicelist,
                display_text=servicetype[0],
                display_order=servicetype[1],
                hours_until_due=servicetype[2],
                show_in_price_table=servicetype[3],
                )
            s.save()
            servicetypes_new.append(s)

        for wordcountrange in ServiceData.wordcountranges:
            w = WordCountRange(
                servicelist=new_servicelist,
                min_words=wordcountrange[0],
                max_words=wordcountrange[1],
                )
            w.save()
            
            for pricepoint in wordcountrange[2]:
                p = PricePoint(
                    wordcountrange=w,
                    servicetype=servicetypes_new[pricepoint[0]],
                    display_order=servicetypes_new[pricepoint[0]].display_order,
                    dollars=pricepoint[1],
                    dollars_per_word=pricepoint[2],
                    is_price_per_word=pricepoint[3],
                    )
                p.save()
