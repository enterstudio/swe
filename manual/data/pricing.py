# Data for creating PriceSet, ServiceType, and WordCountRange

# ServiceType: (ID, text, hours until due, display_on_price_table)
servicetype = [
    (100, 'Free trial: First 250 words', 24, False)
    (101, '24 hours', 24, True),
    (102, '3 days', 72, True),
    (103, '7 days', 7*24, True),
    ]

# wordcountrange: (ID, min, max)
wordcountrange = [
    (1001, None, 500),
    (1002, 500, 1500),
    (1003, 1500, 3000),
    (1004, 3000, 5000),
    (1005, 5000, 7500),
    (1006, 7500, 10000),
    (1007, 10000, 12500),
    (1008, 12500, 15000),
    (1009, 15000, 18000),
    (1010, 18000, None),
    ]

# priceset: (servicetype, wordcountrange, dollars, dollars_per_word, is_price_per_word, is_enabled, hide_on_price_table)
pricepoint = [
    (100, 1001, 0.00, None, False, True, True),
    (101, 1001, 65.00, None, False, True, False),
    (102, 1001, 57.50, None, False, True, False),
    (103, 1001, 50.00, None, False, True, False),
    (100, 1002, 0.00, None, False, True, True),
    (101, 1002, 94.71, None, False, True, False),
    (102, 1002, 83.79, None, False, True, False),
    (103, 1002, 72.86, None, False, True, False),
    (100, 1003, 0.00, None, False, True, True),
    (101, 1003, 139.29, None, False, True, False),
    (102, 1003, 123.21, None, False, True, False),
    (103, 1003, 107.14, None, False, True, False),
    (100, 1004, 0.00, None, False, True, True),
    (101, 1004, 198.71, None, False, True, False),
    (102, 1004, 175.78, None, False, True, False),
    (103, 1004, 152.86, None, False, True, False),
    (100, 1005, 0.00, None, False, True, True),
    (101, 1005, None, None, False, False, False),
    (102, 1005, 241.50, None, False, True, False),
    (103, 1005, 210.00, None, False, True, False),
    (100, 1006, 0.00, None, False, True, True),
    (101, 1006, None, None, False, False, False),
    (102, 1006, 307.21, None, False, True, False),
    (103, 1006, 267.14, None, False, True, False),
    (100, 1007, 0.00, None, False, True, True),
    (101, 1007, None, None, False, False, False),
    (102, 1007, 372.93, None, False, True, False),
    (103, 1007, 324.28, None, False, True, False),
    (100, 1008, 0.00, None, False, True, True),
    (101, 1008, None, None, False, False, False),
    (102, 1008, 438.64, None, False, True, False),
    (103, 1008, 381.43, None, False, True, False),
    (100, 1009, 0.00, None, False, True, True),
    (101, 1009, None, None, False, False, False),
    (102, 1009, 517.50, None, False, True, False),
    (103, 1009, 450.00, None, False, True, False),
    (100, 1010, 0.00, None, False, True, True),
    (101, 1010, None, None, False, False, False),
    (102, 1010, None, None, False, False, False),
    (103, 1010, None, 0.025, True, True, False), 
    ]
