# Data for creating services and prices

class ServiceData:
    # servicetypes = [
    #                 (servicetype_display_text, order, hours_until_due, show_in_price_table), 
    #                 ...
    #                 ]
    servicetypes = [
        ('Free trial: First 250 words', 0, 24, False),
        ('24 hours', 1, 24, True),
        ('3 days', 2, 72, True),
        ('7 days', 3, 7*24, True),
        ]

    # wordcountranges = [
    #                    (min, max, [
    #                             (servicetype_index, dollars, dollars_per_word, is_price_per_word)
    #                             ..., 
    #                             ]),
    #                    ...,
    #                    ]
    # //servicetype_index is based on position in the list above.
    wordcountranges = [
        (None, 500, [
                (0, 0.00, 0.00, False),
                (1, 65.00, 0.00, False),
                (2, 57.50, 0.00, False),
                (3, 50.00, 0.00, False),
                ]),
        (500, 1500, [
                (0, 0.00, 0.00, False),
                (1, 94.71, 0.00, False),
                (2, 83.79, 0.00, False),
                (3, 72.86, 0.00, False),
                ]),
        (1500, 3000, [
                (0, 0.00, 0.00, False),
                (1, 139.29, 0.00, False),
                (2, 123.21, 0.00, False),
                (3, 107.14, 0.00, False),
                ]),
        (3000, 5000, [
                (0, 0.00, 0.00, False),
                (1, 198.71, 0.00, False),
                (2, 175.78, 0.00, False),
                (3, 152.86, 0.00, False),
                ]),
        (5000, 7500, [
                (0, 0.00, 0.00, False),
                (2, 241.50, 0.00, False),
                (3, 210.00, 0.00, False),
                ]),
        (7500, 10000, [
                (0, 0.00, 0.00, False),
                (2, 307.21, 0.00, False),
                (3, 267.14, 0.00, False),
                ]),
        (10000, 12500, [
                (0, 0.00, 0.00, False),
                (2, 372.93, 0.00, False),
                (3, 324.28, 0.00, False),
                ]),
        (12500, 15000, [
                 (0, 0.00, 0.00, False),
                 (2, 438.64, 0.00, False),
                 (3, 381.43, 0.00, False),
                ]),
        (15000, 18000, [
                 (0, 0.00, 0.00, False),
                 (2, 517.50, 0.00, False),
                 (3, 450.00, 0.00, False),
                ]),
        (18000, None, [
                (0, 0.00, 0.00, False),
                (3, 0.00, 0.025, True),
                ]),
        ]
