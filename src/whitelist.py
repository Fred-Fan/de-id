import pandas as pd 
import pickle
import re

debug_word = 'Tylenol'

umls_df = pd.read_csv('whitelist\\umls_LEXICON.csv', delimiter = ',', encoding = 'latin1')
#print umls_df.head()
#print umls_df.columnslatin1



umls_df_crap = umls_df['crap']
#remove nans
umls_df_crap = umls_df_crap[umls_df_crap.notnull()]
#remove numbers
umls_df_crap = umls_df_crap.str.replace('\d+', '')
# # remove single character words
umls_df_crap = umls_df_crap.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ')
#The pattern \b\w\b will replace any single word character with a word boundary
umls_df_crap = umls_df_crap.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# remove rows where length of descriptor is less than 3
umls_df_crap = list(umls_df_crap[umls_df_crap.str.len() > 2])
print(debug_word in umls_df_crap)

#umls_df = umls_df.drop('crap',1)
umls_df_label = umls_df['label']

#remove nans
umls_df_label = umls_df_label[umls_df_label.notnull()]
#remove numbers
umls_df_label = umls_df_label.str.replace('\d+', '')
# # remove single character words
umls_df_label = umls_df_label.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ')
#The pattern \b\w\b will replace any single word character with a word boundary
umls_df_label = umls_df_label.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# remove rows where length of descriptor is less than 3
umls_df_label = list(umls_df_label[umls_df_label.str.len() > 2])
print('label')
print(debug_word in umls_df_label)

#extract the only the initial value of interest
umls_df['happy'] = umls_df['useful'].str.extract('(.*?)\|', expand = True)

umls_df_useful = umls_df['useful']
#remove nans
umls_df_useful = umls_df_useful[umls_df_useful.notnull()]
#remove numbers
umls_df_useful = umls_df_useful.str.replace('\d+', '')
# # remove single character words
umls_df_useful = umls_df_useful.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ').str.replace('|',' ')
#The pattern \b\w\b will replace any single word character with a word boundary
umls_df_useful = umls_df_useful.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# remove rows where length of descriptor is less than 3
umls_df_useful = list(umls_df_useful[umls_df_useful.str.len() > 2])

umls_df_happy = umls_df['happy']
#remove nans
umls_df_happy = umls_df_happy[umls_df_happy.notnull()]
#remove numbers
umls_df_happy = umls_df_happy.str.replace('\d+', '')
# # remove single character words
umls_df_happy = umls_df_happy.str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ').str.replace('{',' ').str.replace('}',' ').str.replace('|',' ')
#The pattern \b\w\b will replace any single word character with a word boundary
umls_df_happy = umls_df_happy.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# remove rows where length of descriptor is less than 3
umls_df_happy = list(umls_df_happy[umls_df_happy.str.len() > 2])


umls_crap_list = list(umls_df_crap)
umls_crap_list = [term.split() for term in umls_crap_list] # convert each string into a list of the words in the string
umls_crap_list = [item for sublist in umls_crap_list for item in sublist] # flatten the list of lists into a single list
umls_crap_list = [i.lower() for i in umls_crap_list]
print(len(set(umls_crap_list)))
print(' ')

umls_label_list = list(umls_df_label)
umls_label_list = [term.split() for term in umls_label_list] # convert each string into a list of the words in the string
umls_label_list = [item for sublist in umls_label_list for item in sublist] # flatten the list of lists into a single list
umls_label_list = [i.lower() for i in umls_label_list]
print(len(set(umls_label_list)))
print(' ')

umls_useful_list = list(umls_df_useful)
umls_useful_list = [term.split() for term in umls_useful_list] # convert each string into a list of the words in the string
umls_useful_list = [item for sublist in umls_useful_list for item in sublist] # flatten the list of lists into a single list
umls_useful_list = [i.lower() for i in umls_useful_list]
print(len(set(umls_useful_list)))
print(' ')

umls_happy_list = list(umls_df_happy)
umls_happy_list = [term.split() for term in umls_happy_list] # convert each string into a list of the words in the string
umls_happy_list = [item for sublist in umls_happy_list for item in sublist] # flatten the list of lists into a single list
umls_happy_list = [i.lower() for i in umls_happy_list]
print(len(set(umls_happy_list)))
print(' ')

umls_list = list(set(umls_crap_list + umls_useful_list + umls_happy_list + umls_label_list))
print(len(set(umls_list)))

print('len set umls_list {}'.format(len(set(umls_list))))
print(debug_word)
print('in umls list')
print(debug_word.lower() in umls_list)

#################
des_mesh_df = pd.read_csv('whitelist\\descriptor_mesh.csv', delimiter = ',', usecols=['type','value'])

# only take the types of data we're potentially interested in
values = ['ENTRY','MH','PA','MS']
des_mesh_df = des_mesh_df.loc[des_mesh_df['type'].isin(values)]

# from the data types that we want, extract the only the initial value of interest
des_mesh_df['descriptor'] = des_mesh_df['value'].str.extract('(.*?)\|', expand = True)
# drop the old 'value' column
des_mesh_df = des_mesh_df.drop('value', 1)
# drop nan's
des_mesh_df = des_mesh_df[des_mesh_df.descriptor.notnull()]
# remove numbers
des_mesh_df['descriptor'] = des_mesh_df['descriptor'].str.replace('\d+', '')
# remove single character words
des_mesh_df['descriptor'] = des_mesh_df['descriptor'].str.replace('-', ' ').str.replace('(',' ').str.replace(')',' ').str.replace('.',' ')
#The pattern \b\w\b will replace any single word character with a word boundary
des_mesh_df['descriptor'] = des_mesh_df['descriptor'].str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
# remove rows where length of descriptor is less than 3
des_mesh_df= des_mesh_df[des_mesh_df['descriptor'].str.len() > 2]

descriptor_mesh_list = list(des_mesh_df['descriptor'])
descriptor_mesh_list = [term.split() for term in descriptor_mesh_list] # convert each string into a list of the words in the string
descriptor_mesh_list = [item for sublist in descriptor_mesh_list for item in sublist] # flatten the list of lists into a single list
descriptor_mesh_list = [i.lower() for i in descriptor_mesh_list]
print(len(set(descriptor_mesh_list)))
print('len set descr_mesh_list {}'.format(len(set(descriptor_mesh_list))))
print(debug_word)
print(debug_word in descriptor_mesh_list)
#print 'tylenol' in descriptor_mesh_list

###############################
mesh_heir = pd.read_csv('whitelist\\MeshTreeHierarchyWithScopeNotes.csv',delimiter = ',', usecols=['Term','Ms']) # Term is the branches
# of the headings in mesh_list, while Ms is a description of that term

mesh_heir_term_list = list(mesh_heir['Term'])
mesh_heir_term_list = [term.split() for term in mesh_heir_term_list] # convert each string into a list of the words in the string
mesh_heir_term_list = [item for sublist in mesh_heir_term_list for item in sublist] # flatten the list of lists into a single list
mesh_heir_term_list = [i.lower() for i in mesh_heir_term_list]

print('len set mesh_heir_term_list {}'.format(len(set(mesh_heir_term_list))))
print(debug_word)
print(debug_word in mesh_heir_term_list)

mesh_heir_ms_list = list(mesh_heir['Ms'])
mesh_heir_ms_list = [term.split() for term in mesh_heir_ms_list if type(term) is str] # convert each string into a list of the words in the string
mesh_heir_ms_list = [item for sublist in mesh_heir_ms_list for item in sublist] # flatten the list of lists into a single list
mesh_heir_ms_list = [i.lower() for i in mesh_heir_ms_list]

print('len set mesh_heir_ms_list {}'.format(len(set(mesh_heir_ms_list))))
print(debug_word)
print(debug_word in mesh_heir_ms_list)

###########################

english_goog = pd.read_csv('whitelist\\20kwords.csv',delimiter = ',') # from https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt
english_goog =  english_goog.head(2050)
english_goog = list(english_goog.word)
english_goog = set([i.lower() for i in english_goog])
names = set(['irael','johnson','scott','steve','charles','ed','richard','william','carolina','christian','smith','thomas','virginia','george','robert','james','microsoft','yahoo'])
# remove names from list of common words
english_goog_list = list(english_goog.difference(names))
# # # remove single character words
english_goog_list = [i.replace(r'\b\w\b', '').replace(r'\s+', ' ') for i in english_goog_list]
#english_goog_list = english_goog_list.str.replace(r'\b\w\b', '').str.replace(r'\s+', ' ')
print(len(english_goog_list))

english_1k = pd.read_csv('whitelist\\1k_words_noNames.csv',delimiter = ',')
english_1k = list(english_1k.word)
english_1k = [i.lower() for i in english_1k]
print(len(english_1k))

english_3k = pd.read_csv('whitelist\\3k_words_noNames.csv',delimiter = ',')
english_3k = list(english_3k.word)
english_3k = [i.lower() for i in english_3k]
print(len(english_3k))

common_english_list = list(set(english_goog_list + english_1k + english_3k))
print(len(common_english_list))
# #############
mesh = pd.read_csv('whitelist\\mtrees2017.txt',delimiter = ';') #high level headings
abbreviations = pd.read_csv('whitelist\\list_of_med_abbreviations.csv', delimiter = ',')
# #print mesh.head()
# #print mesh.columns

# # print abbreviations.head()
# # print abbreviations.columns

mesh_list = list(mesh['Body Regions'])
mesh_list = [term.split() for term in mesh_list] # convert each string into a list of the words in the string
mesh_list = [item for sublist in mesh_list for item in sublist] # flatten the list of lists into a single list
#print mesh_list
mesh_list = [i.lower() for i in mesh_list]
print('len set mesh_list {}'.format(len(set(mesh_list))))
print(debug_word)
print(debug_word in mesh_list)

abbrev_list = list(abbreviations.abbreviation)
abbrev_list = [i for i in abbrev_list if type(i) is str]
abbrev_list = [i.lower() for i in abbrev_list]
print('len set abbrev_list {}'.format(len(set(abbrev_list))))
#print abbrev_list

print(debug_word in abbrev_list)


##########################################
# here are words that keep popping up in the notes that appear safe


words_from_notes_list = ['todays',  'saver', 'crtp', 'sch', 'aud', 'plavix', 'steadily','reconstructions',  'charted', 'pricosec', 'flomax', 'mls', 'neg', 'neb',  'transaminitis', 'hypokinesis', 'tolerating', 'disclaims', 'spoke', 'discrepancies', 'calc', 'paperwork', 'backbleeding',  'recovers', 'lad', 'reconciled', 'audiogram', 
'counseled', 'walgreens',  'afib', 'hydrodiuril',  'edits', 'mgml', 'mgmt', 'diag', 'diagnosishistory',  'notified',  'pmappointment', 'creamcommonly', 'signing', 'mds', 'rt', 'rv', 'rs', 'rx', 'rf', 'rl', 'rm', 'ro','amappointment', 'certifies','westside', 'robitussin', 'hood',  'elevator', 'neobladder', 
 'gyn', 'signup',  'shower',  'tcells',  'lbs', 'pvcs', 'talking', '375mg', 'sulfamethoxazoletrimethoprim', 'paramedics', 'panleukocyte', 'bcells', 'agressive', 'ipss', 'irrigated',  'definitely', 'lpc', 'signatures',  'reschedule', 'hrs', 'pnd', 'claritin', 'benazepril', 'aetiology', 'ventolinproventil', 'dx', 'dw',
 'upreg', 'hypoxemia', 'ems', 'emr', 'psych',  'meshworks', 'gentleman', 'hematogones', 'wc', 'deltasone',  'tfts', 'jello','arteriotomy', 'angiograms', 'mcg',  'hepc', 'neurontin', 'cardiomediastinal', 'dept','dexon', 'cont', 'io',  'zofran', 'meets','stiffener', 'pantcell',
 'lvcs', 'eps', 'urethrotomy', 'mammo', 'yours','sonographer', 'offwhite', 'progressed','mastoids', 'lcd',  'ambulating',  'colacetake', 'bpm', 'bps', 'extrastimuli', 'infrahepatic', 'dorzolamidetimolol', 'prepping', 'painfree', 'bulbocavernous', 'denies', 'cnt',  'floaters', 'aldorenin', 'icd', 'ucsf', 'housestaff',
 'hsv', 'playroom', 'scds', 'andreadis',  'dinner', 'monospot',  'sob', 'omnipaque', 'homogenization', 'verbalizes',  'verbalized',  'appts', 'underestimated', 'unoriented', 'overthecounter',  'anticoag', 'fibroids', 'vicodin',
 'fell','flushed',  'overdue','answered', 'parnassus',  'slash', 'diaphoretic', 'fatigued', 'trouble',  'anesthetized', 'concurs', 'mycophenolate', 'tums', 'bumex', 'shave', 
 'peds', 'pmd',  'pmc', 'pmh',  'consolidations', 'postbiopsy', 'aquaphor', 'asault', 'guardian', 'deo',  'refused', 'wait', 'ekg', 'ptnb', 'hbv', 'valcyte', 'sincerely', 'perm',  'tachycardic', 'checkout',
  'prep', 'sessions', 'solumedrol', 'dermatologist', 'flr',  'soup', 'spr',  'sph', 'orthosurgery',  'intrasinus', 'prelim', 'speaks', 'contraindicated', 'superolateral', 'interoperative',
  'sf', 'refund', 'tty',  'ttp', 'vte', 'vti', 'upstrokes',  'intl', 'moms', 'luken', 'sooner', 'fibroglandular', 'logans','prompted', 'begun', 'approximated',
    'nonafrican', 'plex',  'tomorrow', 'slept', 'electrograms', 'participated',  'sores', 'appreciated','rehab', 'quadrants', 'silhouette', 'advil', 'instructed',
   'rationale', 'pager',  'osteopenia', 'neuro',  'mrn', 'mrg','mlhr','datetime', 'lithotomy', 'surveilance','histories', 'sdi','reps', 'ssi',  'encouraged', 'checks', 'abutting', 
    'tizanidine','yearly', 'betablockers', 'pos', 'hvf', 'birads', 'flowsheetpatient', 'declining', 'wants', 'groins', 
     'consultant', 'ivf', 'compensations', 'ivc', 'consults', 'hent', 'mgdl', 'dilations','hba1c', 'ropivacaine', 'oxycontin', 
     'cialis', 'anesthesiologist',  'kneeling', 'refills', 'proventil',  'dissected', 'mychart', 'mom', 'towel',  'perinephric', 
     'thinks','asap',  'rncomment',  'radiographs',  'discussed', 'ob', 'weekend','sonographic','asst', 'ao', 'maxed', 'rvr', 'stigmata', 'walks', 'girlfriend', 
      'bisected', 'faxed', 'mcal',  'booked', 'complicationsno', 'disp', 'cardiologist', 'polyphagia',  'securely', 'ambien','flowsheets','preop', 'assailants',  'dial', 
       'tdap',  'zostavax', 'bathe','prilosec','postradiation','launch','mirtazapine','stayed', 'wellcontrolled', 'okay','petite', 'tries',  'eats', 'vitals', 'sonograms',
       'bathes', 'basename',  'logan', 'etoh', 'avenue', 'dont','screenings','flonase', 'inch',  'disorderptsd',  'todo',  'colace','bcell',
        'protonix', 'dictations','fidgeting', 'nonlabored','zyprexa','hydrocodoneacetaminophen', 'oxybutynin',  'complained', 'gotten', 'treater','preprocedure','remembers',
        'focally', 'sentences', 'understands',  'uscf', 'wheezes','prepped','reassessed', 'morphologies', 'ambulates', 'guarding', 'deferred', 'prostituting', 'unlabored', 'anymore',
        'retractions', 'thryoid', 'yesterday', 'synopsis','residentfellow', 'bicarb', 'sedated','complains', 'judgement', 'lipitor', 'restroom', 'sfmta', 'accelerations', 'meds',  'lasted','negatives','dictated',
'womens', 'bleeds', 'attends', 'selfharm','stitches', 'motrin',  'collapses',  'percocet', 'extubated', 'uc', 'sickles', 'nighttime', 'nonclinical', 'nap','reportedly', 'calcifications', 'nauseavomiting', 'eval',
'viewsleft','soaks', 'valuables','renalkidney', 'medicalfamily','premed', 'uploaded', 'lasix', 'reopened','ctr', 'whereucsf','addressed', 'preventative','upcoming','zyrtec', 'ucsfmychartorg',
'sig', 'connors','belongings', 'biopsyproven', 'interpreter','dad','sweets', 'lumpectomy', 'witness','await', 'shots', 'grunting', 'levitra', 'straining', 'punctured', 'steet',  'tabs', 'gently', 'reassuring',
 'expires', 'looked', 'approx', 'insync','nebulization', 'combo','hopefully', 'legacy', 'outpt', 'micropuncture', 'admin', 'noncontributory', 'copied', 'username', 'cvs', 'orthopnea', 'transitioned','dosestrength',
  'drips', 'helped', 'nonfasting', 'phd', 'nightly','clipped', 'inheriting', 'discontd', 'benadryl', 'sfgh',  'immunizations', 'underwent', 'shes', 'inhalational', 'trimmed',  'aleve',
  'puts','childrens', 'obliterated', 'cyclobenzaprine', 'forget', 'prozac', 'palpated', 'appt', 'bump', 'yrs','mailed','temp','polysubstance',
   'ins']

#################################
manually_added = ['', '-', '(',')']

# mesh_heir_ms_list seems to contain some phi, not including it for now. mesh_heir_list
whitelist = set(mesh_list + abbrev_list + common_english_list + umls_list  + mesh_heir_term_list +  descriptor_mesh_list + words_from_notes_list + manually_added)
whitelist = set([item for item in whitelist if not item.isdigit()]) # final check to remove all digit-words

print('mesh top nodes list: {}'.format(len(set(mesh_list))))
print('mesh mid nodes list: {}'.format(len(set(mesh_heir_term_list))))
print('mesh descriptors list: {}'.format(len(set(descriptor_mesh_list))))
print('med abbreviations list: {}'.format(len(set(abbrev_list))))
print('common english words list: {}'.format(len(set(common_english_list))))
print('umls scrape list: {}'.format(len(set(umls_list))))
print('ucsf safe words: {}'.format(len(set(words_from_notes_list))))
print('allowable special chars: {}'.format(len(set(words_from_notes_list))))


print('len of final whitelist: {}'.format(len(whitelist)))
print(debug_word)
print('final white')
print(debug_word.lower() in whitelist)

pickle.dump( whitelist, open( "whitelist\\whitelist.pkl", "wb" ) )

# print 'ont list {}'.format(mesh_list)
# print 'abb list {}'.format(abbrev_list)
# print 'eng list {}'.format(engl_list)
# print 'whtlst list {}'.format(whitelist)