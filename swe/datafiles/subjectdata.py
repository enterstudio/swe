#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SubjectData:

    # subjects = [(category_id, category_name,[(topic_id, topic_name, is_active),...]),...]
    subjects = [('Agriculture', [
                ('Agriculture', True),
                ('Agronomy', True),
                ('Animal Science', True),
                ('Conservation', True),
                ('Fish and Wildlife', True),
                ('Food Science and Technology', True),
                ('Forestry', True),
                ('Horticulture', True),
                ('Landscape Architecture', True),
                ('Phytopathology', True),
                ('Phytoproduction', True),
                ('Plant Sciences', True),
                ('Renewable Natural Resources', True),
                ('Soils and Soils Science', True),
                ('Other – Agriculture', True),
                ]),
               ('Astronomy and Planetary Science', [
                ('Astronomy', True),
                ('Cosmology', True),
                ('Planetary Science', True),
                ('Theoretical Astrophysics', True),
                ('Other – Astronomy and Planetary Science', True),
                ]),
               ('Biology', [
                ('Anatomy', True),
                ('Bacteriology', True),
                ('Biochemistry', True),
                ('Bioinformatics', True),
                ('Biological Chemistry', True),
                ('Biophysics', True),
                ('Biostatistics', True),
                ('Biotechnology', True),
                ('Botany', True),
                ('Botany / Plant Science', True),
                ('Cancer Research', True),
                ('Cardiovascular Biology', True),
                ('Cell Biology', True),
                ('Comparative Biology', True),
                ('Computational Biology', True),
                ('Conservation Biology', True),
                ('Developmental Biology', True),
                ('Drug Discovery', True),
                ('Ecology', True),
                ('Entomology', True),
                ('Evolution', True),
                ('Genetics', True),
                ('Genomics', True),
                ('Immunology', True),
                ('Industrial Microbiology', True),
                ('Marine Biology', True),
                ('Microbiology', True),
                ('Molecular Biology', True),
                ('Molecular Epidemiology', True),
                ('Mycology', True),
                ('Neuroscience', True),
                ('Neuroscience – Behavioral / Cognitive', True),
                ('Neuroscience – Cellular / Molecular', True),
                ('Neuroscience – Computational', True),
                ('Neuroscience – Developmental', True),
                ('Neuroscience – Neurobiology of Disease', True),
                ('Ornithology', True),
                ('Parasitology', True),
                ('Pathology', True),
                ('Pharmacology', True),
                ('Proteomics', True),
                ('Stem Cell Biology', True),
                ('Structural Biology', True),
                ('Systems Biology', True),
                ('Taxonomy', True),
                ('Virology', True),
                ('Zoology', True),
                ('Other – Biology', True),
                ]),
               ('Business', [
                ('Accounting', True),
                ('Economics', True),
                ('Finance', True),
                ('Hospitality / Tourism', True),
                ('International Business', True),
                ('Management', True),
                ('Marketing / PR', True),
                ('Patents', True),
                ('Other – Business', True),
                ]),
               ('Chemistry', [
                ('Analytical Chemistry', True),
                ('Applied Chemistry', True),
                ('Biotechnology', True),
                ('Catalysis', True),
                ('Chemical Biology', True),
                ('Chemical Engineering', True),
                ('Computational Chemistry', True),
                ('Crystallography', True),
                ('Drug Discovery', True),
                ('Electrochemistry', True),
                ('Food Science', True),
                ('Inorganic Chemistry', True),
                ('Mass Spectrometry', True),
                ('Materials Chemistry', True),
                ('Materials Science', True),
                ('Nanoscience', True),
                ('Nuclear Chemistry', True),
                ('Organic Chemistry', True),
                ('Pharmaceutical Chemistry', True),
                ('Physical Chemistry', True),
                ('Polymer Science', True),
                ('Spectroscopy', True),
                ('Theoretical Chemistry', True),
                ('Other – Chemistry', True),
                ]),
               ('Computer Science and Engineering', [
                ('Algorithms and Data Structures', True),
                ('Artificial Intelligence', True),
                ('Computer and Information Sciences', True),
                ('Computer Architecture and Engineering', True),
                ('Concurrency', True),
                ('Formal Methods', True),
                ('Graphics and Visualization', True),
                ('Information Science and Systems', True),
                ('Information Theory', True),
                ('Management Information Systems', True),
                ('Programming Languages', True),
                ('Security and Cryptography', True),
                ('Systems Analysis', True),
                ('Other – Computer Science and Engineering', True),
                ]),
               ('Engineering', [
                ('Acoustics', True),
                ('Aeronautical Engineering', True),
                ('Astronautical Engineering', True),
                ('Architecture', True),
                ('Automotive Engineering', True),
                ('Bioengineering', True),
                ('Biomechanics', True),
                ('Biomedical Engineering', True),
                ('Chemical Engineering', True),
                ('Civil Engineering', True),
                ('Communications', True),
                ('Computer Engineering', True),
                ('Electrical Engineering', True),
                ('Electronics', True),
                ('Environmental Engineering', True),
                ('Fluid Mechanics / Rheology', True),
                ('Hydraulic / Hydrologic Engineering', True),
                ('Industrial Engineering', True),
                ('Manufacturing', True),
                ('Materials Engineering', True),
                ('Materials Science', True),
                ('Mechanical Engineering', True),
                ('Mining', True),
                ('Nuclear Engineering', True),
                ('Ocean Engineering', True),
                ('Petroleum Engineering', True),
                ('Robotics / Controls', True),
                ('Signal Processing', True),
                ('Software Engineering', True),
                ('Solid Mechanics', True),
                ('Structural Engineering', True),
                ('Systems Engineering', True),
                ('Tissue Engineering', True),
                ('Transportation', True),
                ('Other – Engineering', True),
                ]),
               ('Earth and Environmental Science', [
                ('Agriculture', True),
                ('Agronomy', True),
                ('Atmospheric Science', True),
                ('Cartography', True),
                ('Climatology', True),
                ('Earth Science', True),
                ('Environmental Science', True),
                ('Forestry', True),
                ('Geochemistry', True),
                ('Geographic Information Systems', True),
                ('Geography', True),
                ('Geology', True),
                ('Geophysics', True),
                ('Geoscience', True),
                ('Hydrology', True),
                ('Meteorology', True),
                ('Oceanography', True),
                ('Paleoclimatology', True),
                ('Paleontology', True),
                ('Planetary Geology', True),
                ('Seismology', True),
                ('Surveying', True),
                ('Other – Earth and Environmental Science', True),
                ]),
               ('Mathematics', [
                ('Analysis', True),
                ('Applied Mathematics', True),
                ('Combinatorics', True),
                ('Foundations and Logic', True),
                ('Geometry and Topology', True),
                ('Numerical Analysis', True),
                ('Statistics', True),
                ('Other – Mathematics', True),
                ]),
               ('Medicine and Health', [
                ('Allergy', True),
                ('Anatomy', True),
                ('Anesthesiology', True),
                ('Audiology', True),
                ('Cancer / Oncology', True),
                ('Cardiac Electrophysiology', True),
                ('Cardiology – Interventional', True),
                ('Cardiology – Noninvasive', True),
                ('Cardiology and Circulation', True),
                ('Childhood Development', True),
                ('Clinical Genetics', True),
                ('Clinical Immunology', True),
                ('Clinical Pharmacology', True),
                ('Clinical Psychology', True),
                ('Clinical Trials', True),
                ('Communication Disorders', True),
                ('Critical Care Medicine', True),
                ('Dental / Oral Surgery', True),
                ('Dentistry', True),
                ('Dermatology', True),
                ('Developmental Psychology', True),
                ('Diabetes', True),
                ('Emergency Medicine', True),
                ('Endocrinology', True),
                ('Epidemiology', True),
                ('Family Medicine', True),
                ('Gastroenterology', True),
                ('General Medicine', True),
                ('Geriatrics', True),
                ('Gerontology', True),
                ('Gynecology', True),
                ('Health and Medical Services', True),
                ('Health Economics and Outcomes Research', True),
                ('Hematology', True),
                ('Hematology – Oncology', True),
                ('Hepatology', True),
                ('Histology', True),
                ('Hypertension', True),
                ('Infectious Diseases', True),
                ('Internal Medicine', True),
                ('Maternal and Fetal Medicine', True),
                ('Medical Physics', True),
                ('Medical Laboratory Sciences and Services', True),
                ('Medical Technology', True),
                ('Mental Health', True),
                ('Metabolism', True),
                ('Midwifery', True),
                ('Molecular Epidemiology', True),
                ('Neonatal / Perinatal Medicine', True),
                ('Nephrology', True),
                ('Neurology', True),
                ('Neurology – Child', True),
                ('Nuclear Medicine', True),
                ('Nursing', True),
                ('Nursing Technology', True),
                ('Nutrition', True),
                ('Obstetrics', True),
                ('Occupational Medicine', True),
                ('Oncology – Medical', True),
                ('Oncology – Radiation', True),
                ('Oncology – Surgical', True),
                ('Optometry', True),
                ('Ophthalmology', True),
                ('Orthopedics', True),
                ('Osteopathic Medicine', True),
                ('Otolaryngology', True),
                ('Pain Medicine', True),
                ('Palliative Medicine', True),
                ('Pathology', True),
                ('Pediatrics', True),
                ('Pharmacology', True),
                ('Pharmacy', True),
                ('Physical and Rehabilitative Medicine', True),
                ('Physiology', True),
                ('Plastic Surgery', True),
                ('Podiatry', True),
                ('Preventive Medicine', True),
                ('Psychiatry', True),
                ('Psychiatry – Addiction / Substance Abuse', True),
                ('Psychiatry – Child', True),
                ('Psychiatry – General', True),
                ('Psychiatry – Geriatric', True),
                ('Psychology', True),
                ('Public Health', True),
                ('Pulmonary Disease', True),
                ('Radiation', True),
                ('Radiobiology', True),
                ('Radiology', True),
                ('Reproductive Biology', True),
                ('Rheumatology', True),
                ('Sexual Dysfunction', True),
                ('Social Work', True),
                ('Speech / Language Pathology', True),
                ('Spinal Cord Injury', True),
                ('Sports Medicine', True),
                ('Stem Cell Biology', True),
                ('Surgery – General', True),
                ('Surgery – Specialist', True),
                ('Toxicology', True),
                ('Transplantation', True),
                ('Tropical Medicine', True),
                ('Urology', True),
                ('Veterinary Science', True),
                ('Virology', True),
                ('Other – Medicine and Health', True),
                ]),
               ('Physics', [
                ('Atomic and Molecular Physics', True),
                ('Biological Physics', True),
                ('Chemical Physics', True),
                ('Computational Physics', True),
                ('Condensed Matter Physics', True),
                ('Elementary Particles', True),
                ('Fluid Mechanics', True),
                ('High Energy Physics', True),
                ('Materials Physics', True),
                ('Materials Science', True),
                ('Medical Physics', True),
                ('Nanoscience', True),
                ('Nuclear Physics', True),
                ('Optics / Lasers', True),
                ('Plasma Physics', True),
                ('Solid-state Physics', True),
                ('Theoretical Physics', True),
                ('Other – Physics', True),
                ]),
               ('Humanities and Social Science', [                        
                ('Anthropology', True),
                ('Archeology', True),
                ('Architecture', True),
                ('Communications', True),
                ('Criminal Justice and Corrections', True),
                ('Criminology', True),
                ('Economics', True),
                ('Economics – International', True),
                ('Economics – Macro', True),
                ('Economics – Micro', True),
                ('Education', True),
                ('Environmental Policy', True),
                ('Ethics', True),
                ('Government', True),
                ('History', True),
                ('International Relations', True),
                ('Language', True),
                ('Law', True),
                ('Law – International', True),
                ('Library / Information Science', True),
                ('Linguistics', True),
                ('Philosophy', True),
                ('Policy', True),
                ('Political Science', True),
                ('Political Science – Comparative', True),
                ('Political Science – International', True),
                ('Political Theory', True),
                ('Public Administration', True),
                ('Public Finance and Fiscal Policy', True),
                ('Publishing / Media', True),
                ('Religious Studies', True),
                ('Sociology', True),
                ('Urban Studies', True),
                ('Women\'s Studies', True),
                ('Other – Humanities and Social Science', True),
                ]),
               ('Other Fields', [
                ('Science – General', True),
                ('Other', True),
                ]),
        ]
