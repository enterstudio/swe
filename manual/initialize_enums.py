from swe.models import Subject

subjects = [
    (1, 'Anthropology', True),
    (2, 'Biology', True),
    (3, 'Zoology', True),
    ]

for subject in subjects:
    s = Subject(
        subject_id=subject[0],
        display_text=subject[1],
        enabled=subject[2],
        )
    s.save()

#--------------------------------------
from swe.models import ServiceType

servicetypes = [
    (1, '24 hours', 24, True),
    (2, '3 days', 72, True),
    (3, '7 days', 7*24, True),
    ]

for servicetype in servicetypes:
    s = ServiceType(
        service_type_id = servicetype[0],
        display_text = servicetype[1],
        hours_until_due = servicetype[2],
        enabled=servicetype[3],
        )
    s.save()

#--------------------------------------
from swe.models import WordCountRange

wordcountranges = [
    (1, None, 2500, True),
    (2, 2500, 5000, True),
    (3, 5000, 7500, True),
    (4, 7500, 10000, True),
    (5, 10000, 15000, True),
    (6, 15000, None, True),
    ]

for wordcountrange in wordcountranges:
    w = WordCountRange(
        word_count_range_id = wordcountrange[0],
        min_words = wordcountrange[1],
        max_words = wordcountrange[2],
        enabled = wordcountrange[3],
        )
    w.save()
