'''
Authors:
Sheetal Krishna Mohanadas Janaki - U1135144
Greeshma Mahadeva Prasad - U1141804
'''

import sys
import re
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import svm
from sklearn import linear_model
import numpy as np
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.tag.stanford import CoreNLPNERTagger
from nltk.tag.stanford import CoreNLPPOSTagger
import os

incidentTags={'ARSON':0,'ATTACK':1,'BOMBING':2,'KIDNAPPING':3,'ROBBERY':4}

# Change the path according to your system
#stanford_classifier = 'C:\Python3.5\stanford-ner-2017-06-09\classifiers\english.all.3class.distsim.crf.ser.gz'
stanford_classifier = 'C:\\Users\Mohanadas\AppData\Roaming\Python\stanford-ner-2017-06-09\stanford-ner-2017-06-09\classifiers\english.all.3class.distsim.crf.ser.gz'
#stanford_ner_path = 'C:\Python3.5\stanford-ner-2017-06-09\stanford-ner.jar'
stanford_ner_path = "C:\\Users\Mohanadas\AppData\Roaming\Python\stanford-ner-2017-06-09\stanford-ner-2017-06-09\stanford-ner.jar"

#stanford_classifier = os.environ.get('STANFORD_MODELS').split(':')[0]

# For getting the path for StanfordNERTagger 
#stanford_ner_path = os.environ.get('CLASSPATH').split(':')[0]

# Creating Tagger Object


#print ('Hi! This is an information extractor. Please enter your file like:\n')
#cmdLineArgs = input('infoextract input.txt\n')
#cmdLineArgs = cmdLineArgs.split()

try:
    with open(sys.argv[1], 'r') as file:
        fileContent = file.read().strip()
        #split based on id pattern
        articles = list(filter(None, re.split(r"(((DEV-MUC3-)|(TST1-MUC3-)|(TST2-MUC4-))[0-9]{4})", fileContent)))
    file.close()

except BaseException as e:
    if str(e)!="":
        print('Unable to open the file OR file doesn\'t exist. \n Detailed exception is: \n'+str(e)+"\n")
        sys.exit()

#Create a dictionary of ids and articles
news_dictionary = {}
outputFile = open(sys.argv[1]+".templates" , "w")

listOfIds =[]
for article in articles:
    id_pattern = re.compile("(((DEV-MUC3-)|(TST1-MUC3-)|(TST2-MUC4-))[0-9]{4})")
    if id_pattern.match(article):
      id = article
      continue
    half_id_pattern = re.compile("((DEV-MUC3-)|(TST1-MUC3-)|(TST2-MUC4-))")
    if half_id_pattern.match(article):
      continue
    listOfIds.append(id)
    news_dictionary[id] = article

def getClassifier():
    try:
        with open('AllAnswers.txt', 'r') as file:
            fileContent = file.read().strip()
            incident_list_train = []
            # split based on id pattern
            articles = list(filter(None, re.split(r"INCIDENT:", fileContent)))
            for article in articles:
                if article.startswith('ID'):
                    continue
                incident_list_train.append(incidentTags[article.split('\n')[0].strip()])
        file.close()

    except BaseException as e:
        if str(e) != "":
            print(
                'Unable to open the AllAnswers file OR file doesn\'t exist. \n Detailed exception is: \n' + str(e) + "\n")
            sys.exit()

    try:
        with open('AllTexts.txt', 'r') as file:
            fileContent = file.read().strip()
            # split based on id pattern
            articles = list(filter(None, re.split(r"(((DEV-MUC3-)|(TST1-MUC3-)|(TST2-MUC4-))[0-9]{4})", fileContent)))
            news_list_train = {}
            id_pattern = re.compile("(((DEV-MUC3-)|(TST1-MUC3-)|(TST2-MUC4-))[0-9]{4})")
            half_id_pattern = re.compile("((DEV-MUC3-)|(TST1-MUC3-)|(TST2-MUC4-))")
            for article in articles:
                if id_pattern.match(article):
                    continue
                if half_id_pattern.match(article):
                    continue
                news_list_train[article] = incident_list_train[len(news_list_train)]

        file.close()

    except BaseException as e:
        if str(e) != "":
            print('Unable to open the AllTexts file OR file doesn\'t exist. \n Detailed exception is: \n' + str(e) + "\n")
            sys.exit()







    # splitting process for classifier
    split_news_list_train = np.array_split(list(news_list_train), 5)
    '''The above will contain dtype attributes like this:-
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'] on splitting results in--
    [array(['a', 'b', 'c', 'd'], dtype='<U1'), array(['e', 'f', 'g'], dtype='<U1'), array(['h', 'i', 'j'], dtype='<U1')]
    To eliminate this, we convert item to a list to get something like:
    [['a', 'b', 'c', 'd'], ['e', 'f', 'g'], ['h', 'i', 'j']]
    '''
    split_news_list_train = [list(x) for x in split_news_list_train]

    highestAccuracyClassifier = 0
    highestAccuracy = 0
    #text_clf = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), ('clf', svm.SVC(kernel='linear'))])
    text_clf = Pipeline([('vect', CountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         ('clf', linear_model.SGDClassifier(alpha=0.0001, average=False, class_weight=None, epsilon=0.1,
                  eta0=0.0, fit_intercept=True, l1_ratio=0.15,
                  learning_rate='optimal', loss='hinge', max_iter=None, n_iter=None,
                  n_jobs=1, penalty='l2', power_t=0.5, random_state=None,
                  shuffle=True, tol=None, verbose=0, warm_start=False))])

    for part in split_news_list_train:
        trainArtSet = list(
            set(news_list_train) - set(part))  # gets everything left in the news set minus the test set a.k.a 'part'
        trainTagSet = [news_list_train[x] for x in trainArtSet]
        text_clf.fit(trainArtSet, trainTagSet)
        testArtSet = part
        predicted = text_clf.predict(testArtSet)
        if np.mean(predicted == [news_list_train[x] for x in testArtSet]) > highestAccuracy:
            highestAccuracy = np.mean(predicted == [news_list_train[x] for x in testArtSet])
            highestAccuracyClassifier = text_clf
    return highestAccuracyClassifier

def getWeapon(article):
    weapons = {}

    weapons["GUN"] = ["MACHINE-GUN", "MACHINE-GUNS", "MACHINEGUN", " MACHINEGUNS", "SUB-MACHINE-GUNS", "SUB-MACHINEGUN",
                      "SUB-MACHINEGUNS", "SUBMACHINEGUN", "SUBMACHINEGUNS", "SUBMACHINE-GUN", "SUBMACHINE-GUNS",
                      "SUB-MACHINE-GUN",
                      "GUN ", "GUNS", "MACHINEGUN", "MACHINEGUNS", "SUBMACHINE GUN", "SUBMACHINE GUNS",
                      "SUB MACHINE GUN", "SUB MACHINE GUNS",
                      "HAND-GUN", "HAND-GUNS", "AIR GUN", "AIRGUN", "AIR-GUN", "AIR GUNS", "AIRGUNS", "AIR-GUNS",
                      "HANDGUN", "HANDGUNS", "HAND GUN",
                      "HAND GUNS", "BLOWGUN", "BLOWGUNS", "GUNPOWDER", "GUN-POWDER"]

    weapons["BOMB"] = ["POWERFUL BOMB", "BOMBS", "BOMB", "AERIAL BOMB ", "BOMB", "BOMBS", "CARBOMB", "CAR BOMB",
                       "CAR-BOMB", "TERRORIST BOMB", "TERRORIST BOMBS",
                       "TERRORIST-BOMB", "TERRORIST-BOMBS", "HOME-MADE BOMB", "HOMEMADE BOMB", "BUSBOMB", "BUSBOMBS",
                       "BUS-BOMB", "STONE", "BUS BOMB", "INCENDIARY BOMB",
                       "TRUCK-BOMB", "TRUCK BOMB", "PLASTIC BOMB", "PLASTIC-BOMB"]

    weapons["DYNAMITE"] = ["DYNAMITE", "DYNAMITE-ATTACK", "DYNAMITE-ATTACKS", "DYNAMITE ATTACK", "DYNAMITE ATTACKS",
                           "DYNAMITE STICK", "DYNAMITE STICKS", "DYNAMITE CHARGE",
                           "DYNAMITE-STICK", "DYNAMITE-STICKS", "DYNAMITES", "DYNAMITE CHARGE"]

    weapons["EXPLOSIVE"] = ["EXPLOSIVE DEVICES","EXPLOSIVE", "EXPLOSIVES", "VEHICLE LOADED WITH EXPLOSIVES", "EXPLOSIVE DEVICE",
                            "EXPLOSIVE DEVICES", "EXPLOSIVE-DEVICE",
                            "EXPLOSIVE-DEVICES"]

    weapons["GRENADE"] = ["GRENADES", "GRENADE", "HANDGRENADE", "HANDGRENADES", "HAND-GRENADE", "HAND-GRENADES",
                          "HAND GRENADE", "HAND-GRENADE",
                          "HAND-GRENADES", "HAND GRENADES"]

    weapons["BULLET"] = ["BULLET ", "BULLETS"]

    weapons["AK-47"] = ["AK-47S", "AK-47"]
    weapons["MORTAR"] = ["MORTAR", "MORTARS"]
    weapons["ROCKET"] = ["ROCKET", "ROCKETS"]

    weapons["RIFLE"] = ["AK RIFLES", "RIFLE", "RIFLES", "AK-47 RIFLE", "AK-47 RIFLES", "ASSAULT RIFLE", "ASSAULT-RIFLE"]

    weapons["MISC"] = ["MOLOTOV COCKTAILS", "STONES", "ARTILLERY","FIREARMS", "FIREARM","PROJECTILE", "TNT", "RDX"]

    weapons["PISTOL"] = ["PISTOLS", "PISTOL"]

    weapons["REVOLVER"] = ["REVOLVER", "REVOLVERS"]

    weapons["FIRE ARM"] = ["FIRE-ARM", "FIRE ARM"]

    weapons["TANK"] = ["GAS TANKS", "TANK", "TANKER"]

    weapons["GUNPOWDER"] = ["GUNPOWDER", "GUN-POWDER"]

    '''listOfWeapons = "MACHINE-GUN, MACHINE-GUNS, MACHINEGUN,  MACHINEGUNS, GRENADES, GRENADE, " \
                "HANDGRENADE,HANDGRENADES, HAND-GRENADE, HAND-GRENADES, BULLET , BULLETS, " \
                "AK-47S, AK-47, A BOMB, THE BOMB, BOMB, BOMBS,MORTAR,MORTARS, ROCKET, ROCKETS, SUB-MACHINE-GUN, " \
                "SUB-MACHINE-GUNS, SUB-MACHINEGUN, SUB-MACHINEGUNS, SUBMACHINEGUN, SUBMACHINEGUNS,SUBMACHINE-GUN, SUBMACHINE-GUNS " \
                "AK RIFLES, RIFLE, RIFLES, AK-47 RIFLE, AK-47 RIFLES, STONES, MORTAR, MORTARS, " \
                "GUN , GUNS, MACHINEGUN MACHINEGUNS, SUBMACHINE GUN, SUBMACHINE GUNS, SUB MACHINE GUN, " \
                "SUB MACHINE GUNS, HAND GRENADE, HAND-GRENADE, HAND-GRENADES,HAND GRENADES," \
                "AERIAL BOMB ,ARTILLERY, PISTOLS, PISTOL,HANDGUN, HANDGUNS, HAND GUN, HAND GUNS, " \
                "HAND-GUN, HAND-GUNS, AIR GUN, AIRGUN, AIR-GUN, AIR GUNS, AIRGUNS, AIR-GUNS, " \
                "REVOLVER, REVOLVERS, BLOWGUN, BLOWGUNS, ASSAULT RIFLE, ASSAULT-RIFLE, FIREARM, " \
                "FIRE-ARM, FIRE ARM, TANK, TANKER,DYNAMITE,DYNAMITE-ATTACK, DYNAMITE-ATTACKS,DYNAMITE ATTACK, DYNAMITE ATTACKS, DYNAMITE STICK, DYNAMITE STICKS, DYNAMITE-STICK, DYNAMITE-STICKS, DYNAMITES, BOMB, BOMBS, EXPLOSIVE, " \
                " ROCKET,ROCKETS, GRENADE, CARBOMB, CAR BOMB, CAR-BOMB, GRENADES, EXPLOSIVES, " \
                "TERRORIST, TERRORIST BOMB, TERRORIST BOMBS, TERRORIST-BOMB,TERRORIST-BOMBS, MINE, ROCKET, HOMEMADE BOMB, HOME-MADE BOMB,STONES, BUSBOMB, VEHICLE LOADED WITH EXPLOSIVES," \
                "BUSBOMBS, BUS-BOMB, STONE, BUS BOMB, INCENDIARY BOMB, MINES, EXPLOSIVE DEVICE,EXPLOSIVE DEVICES,EXPLOSIVE-DEVICE,EXPLOSIVE-DEVICES, " \
                "DYNAMITE CHARGE, TRUCK-BOMB, PROJECTILE, TNT, RDX, TRUCK BOMB, FIRE,PLASTIC BOMB, PLASTIC-BOMB,TNT, GUNPOWDER, GUN-POWDER"


    #article = nltk.pos_tag(word_tokenize(article))
    article = CoreNLPPOSTagger(url='http://localhost:9000').tag(word_tokenize(article))
    article = [w for w in article if not w in stopwords.words('english')]
    weaponsContained = []
    for i,taggedWord in enumerate(article):
        if taggedWord[1].startswith('N'):
            try:
                word = taggedWord[0]
                for weapon in listOfWeapons.split(','):
                    if weapon.strip() in word:
                        #now, to get the full weapon, we need all the nouns immediately preceeding it and the adjectives preceeding the noun and the nouns suceeding the word
                        adjNouns = []
                        j=i-1
                        while article[j][1].startswith('N'):
                            adjNouns.append(article[j][0])
                            j-=1
                        while article[j][1].startswith('J'):
                            adjNouns.append(article[j][0])
                            j -= 1
                        #numbers as well like 4 huge guns
                        while article[j][1] == 'CD':
                            adjNouns.append(article[j][0])
                            j -= 1
                        while article[j][1] == 'DT':
                            adjNouns.append(article[j][0])
                            j -= 1
                        adjNouns =  " ".join(reversed(adjNouns)).split()
                        adjNouns.append(word)
                        #Find noun phrases that follow the weapon as well
                        j=i+1
                        while article[j][1].startswith('N'):
                            adjNouns.append(article[j][0])
                            j+=1
                        adjNouns = ' '.join(adjNouns)
                        if adjNouns not in weaponsContained:
                            weaponsContained.append(adjNouns)
            except BaseException as e:
                continue
    '''
    weaponsContained = []
    categories=list(weapons.keys())
    for category in categories:
        for weapon in weapons[category]:
            if ((" " not in weapon.strip() and weapon.strip() in article.split()) or (" " in weapon.strip() and (" "+weapon+" ") in article)) and weapon.strip() not in weaponsContained:
                weaponsContained.append(weapon.strip())
                if category != 'MISC':
                    break


    return weaponsContained

def getOrganization(article):
    organizations={}
    organizations["MRTA"] = ["TUPAC AMARU REVOLUTIONARY MOVEMENT", "TUPAC AMARY REVOLUTIONARY MOVEMENT","MRTA"]
    organizations["FPM"] = ["MORAZANIST PATRIOTIC FRONT", "FPM"]
    organizations["OWL"] = ["OWL", "OWLS"]
    organizations["FMLN"] = ["FARABUNDO MARTI NATIONAL LIBERATION FRONT", "FMLN", "FARABUNDO MARTI NATIONAL LIBERATION FRONT [FMLN]","FARABUNDO MARTI NATIONAL LIBERATION FRONT (FMLN)","SALVADORAN GUERRILLAS",'THE FMLN [FARABUNDO MARTI NATIONAL LIBERATION MOVEMENT]']
    organizations["ARENA"] = ["ARENA [NATIONALIST REPUBLICAN ALLIANCE] GOVERNMENT", "ARENA", "THE ARENA [NATIONALIST REPUBLICAN ALLIANCE]","ARENA [NATIONALIST REPUBLICAN ALLIANCE]", "NATIONALIST REPUBLICAN ALLIANCE"]
    organizations["ELN"] = ["ELN","COLOMBIAN NATIONAL LIBERATION ARMY","NATIONAL LIBERATION ARMY", 'THE NATIONAL LIBERATION ARMY',"CAMILIST UNION - ARMY OF NATIONAL LIBERATION ELN","CAMILIST UNION - ARMY OF NATIONAL LIBERATION","ELN [ARMY OF NATIONAL LIBERATION]", "THE ARMY OF NATIONAL LIBERATION","ARMY OF NATIONAL LIBERATION","COLOMBIAN SUBVERSIVE GROUP" ,"CASTROITE ARMY OF NATIONAL LIBERATION (ELN)" ,"COLOMBIAN GUERRILLA GROUP","THE GUERRILLA ARMY OF NATIONAL LIBERATION","PRO-CASTROITE ARMY OF NATIONAL LIBERATION"]
    organizations["FPMR"] = ["MANUEL RODRIGUEZ PATRIOTIC FRONT", "FPMR",'THE COMMUNIST PARTY OF CHILE', "COMMUNIST PARTY OF CHILE", "COMMUNIST PARTY","PCCH"]
    organizations["POLICE"] = ["SALVADORAN POLICE", "COLOMBIAN POLICE"]
    organizations["ESA"]=["ESA","SECRET ANTICOMMUNIST ARMY" ,"GUATEMALA'S PROGRESSIVE PATRIOTS"]
    organizations["ARMY"] = ["CRISTIANI'S GOVERNMENT","FORCES OF THE CRISTIANI ADMINISTRATION", "SALVADORAN ARMY MILITARY SCHOOL","SALVADORAN ARMED FORCES", "ARMED FORCES HIGH COMMAND", "ARMED FORCES", "SALVADORAN TOP MILITARY COMMAND","THE MILITARY FASCIST DICTATORSHIP","ULTRALEFTIST GROUPS","SALVADORAN ARMED FORCES","MILITARY OFFICERS", "EIGHT MILITARY OFFICERS","ATLACATL BATTALION", "ARMED FORCES","ARMED FORCES' GENERAL STAFF", "ARMED FORCES", "GENERAL STAFF","SALVADORAN ARMY", "GOVERNMENT AND ARMY", "GOVERNMENT AND ARMY SECTORS"]
    organizations["VIDES"]=["VIDES CASANOVA'S TROOPS AND COMMANDING OFFICERS","JUAN RAFAEL BUSTILLO'S TROOPS","JOSE NAPOLEON DUARTE'S TROOPS"]
    organizations["RIGHTWING"] = ["DEATH SQUADS","DEATH SQUAD", "ULTRARIGHTIST FACTIONS", "EXTREME RIGHT-WING ASSASSINATION GROUP", "FAR RIGHTWING", "RIGHTWING", "ASSASSINATION GROUP"]
    organizations["CEA"] = ["SPECIAL ARMED CORPS [CUERPO ESPECIAL ARMADO], CEA", "SPECIAL ARMED CORPS [CUERPO ESPECIAL ARMADO]", "SPECIAL ARMED CORPS", "CUERPO ESPECIAL ARMADO", "CEA", "THE ELITE FORCE"]
    organizations["AIRFORCE"] = ["SALVADORAN AIR FORCE", "AIR FORCE"]
    organizations["MEDELLIN"] = ["MEDELLIN CARTEL", "DRUG TRAFFICKING ORGANIZATION","THE MEDELLIN CARTEL'S ARMED WING", "MEDELLIN", "EXTRADITABLES","THE EXTRADITABLES"]
    organizations["COLSEC"] = ["THE COLOMBIAN INTELLIGENCE SERVICES", "THE COLOMBIAN SECURITY SERVICES"]
    organizations["GERARDO"]=["GERARDO BARRIOS COMMANDO UNIT","GERARDO BARRIOS CIVIC FORCE"]
    organizations["FARC"]=['REVOLUTIONARY ARMED FORCES OF COLOMBIA','FARC', 'FARC 12TH FRONT']
    organizations['FAL']=["FAL","ZARATE WILKA ARMED FORCES OF LIBERATION" ,"FAL-ZARATE WILKA GROUP / ZARATE WILKA GROUP"]
    organizations['NARCO']=["NARCOMILITARY ORGANIZATIONS" ,"RIGHT-WING PARAMILITARY GROUPS"]
    organizations["MISC"] =['[DIGNITY] BATTALIONS','1ST INFANTRY BRIGADE','DRUG MAFIA','BREAD','BREAD, LAND, WORK, AND FREEDOM MOVEMENT','BASQUE FATHERLAND AND LIBERTY [ETA] SEPARATIST ORGANIZATION', 'SENDERO LUMINOSO', 'MAOIST POPULAR LIBERATION ARMY', 'UMOPAR', '19-APRIL MOVEMENT', 'CRISTIANI GOVERNMENT', 'NATIONAL PARTY', 'DRUG TRAFFICKING GANGS', "PEOPLE'S REVOLUTIONARY ARMY",'SHINING PATH', 'LOS EXTRADITABLES', 'U.S. CIA', '6TH MILITARY DETACHMENT', 'SALVADORAN REGIME',  'COCAINE CARTELS', 'SPECIAL ARMED CORPS [CUERPO ESPECIAL ARMADO]']
    #organizations = ['MORAZANIST PATRIOTIC FRONT', ' CEA', 'FORCES OF THE CRISTIANI ADMINISTRATION', '[DIGNITY] BATTALIONS', 'SALVADORAN POLICE', '1ST INFANTRY BRIGADE', 'TUPAC AMARU REVOLUTIONARY MOVEMENT', 'ELN', 'DRUG MAFIA', 'BREAD, LAND, WORK, AND FREEDOM MOVEMENT', 'MEDELLIN CARTEL', 'PCCH', 'NATIONAL LIBERATION ARMY', 'SALVADORAN ARMY', 'BASQUE FATHERLAND AND LIBERTY [ETA] SEPARATIST ORGANIZATION', 'SENDERO LUMINOSO', 'THE COLOMBIAN INTELLIGENCE SERVICES', 'CUERPO ESPECIAL ARMADO', 'FMLN', 'MILITARY OFFICERS', 'FPMR', 'MRTA', 'GENERAL STAFF', 'MAOIST POPULAR LIBERATION ARMY', 'ARMED FORCES DEATH SQUADS', 'FARABUNDO MARTI NATIONAL LIBERATION FRONT (FMLN)', 'EXTRADITABLES', 'AIR FORCE', 'CEA', 'NATIONAL POLICE', 'COMMUNIST PARTY OF CHILE', 'DRUG TRAFFICKING ORGANIZATION', 'DEATH SQUAD', 'BREAD', 'THE MILITARY FASCIST DICTATORSHIP', 'SALVADORAN GUERRILLAS', 'ATLACATL BATTALION', 'UMOPAR', 'ASSASSINATION GROUP', '19-APRIL MOVEMENT', 'THE OWLS', 'SALVADORAN ARMED FORCES', "THE MEDELLIN CARTEL'S ARMED WING", 'MILITARY', 'SALVADORAN GOVERNMENT', 'RIGHTWING', 'OWLS', 'SALVADORAN TOP MILITARY COMMAND', 'CRISTIANI GOVERNMENT', 'SALVADORAN ARMY MILITARY SCHOOL','MEDELLIN', 'THE ELITE FORCE', 'EIGHT MILITARY OFFICERS', 'COMMUNIST PARTY', 'SALVADORAN AIR FORCE', 'PRO-CASTROITE ARMY OF NATIONAL LIBERATION', 'COLOMBIAN POLICE', 'EXTREME RIGHT-WING ASSASSINATION GROUP', 'THE EXTRADITABLES', 'NATIONAL PARTY', 'DRUG TRAFFICKING GANGS', "PEOPLE'S REVOLUTIONARY ARMY", 'SPECIAL ARMED CORPS', 'THE SALVADORAN AIR FORCE', 'COLOMBIAN GUERRILLA GROUP', "ARMED FORCES' GENERAL STAFF", 'TUPAC AMARY REVOLUTIONARY MOVEMENT', 'SHINING PATH', 'FPM', 'FARABUNDO MARTI NATIONAL LIBERATION FRONT [FMLN]', 'ARMED FORCES', 'THE COLOMBIAN SECURITY SERVICES', 'FMLN ', 'ULTRALEFTIST GROUPS', 'LOS EXTRADITABLES', 'U.S. CIA', 'THE COMMUNIST PARTY OF CHILE', 'FARABUNDO MARTI NATIONAL LIBERATION FRONT', 'ELN [ARMY OF NATIONAL LIBERATION]', 'MANUEL RODRIGUEZ PATRIOTIC FRONT', '6TH MILITARY DETACHMENT', 'THE MEDELLIN CARTEL', 'SALVADORAN REGIME', "CRISTIANI'S GOVERNMENT", 'FARC 12TH FRONT', 'ARMY OF NATIONAL LIBERATION', 'THE NATIONAL LIBERATION ARMY', 'COCAINE CARTELS', 'SPECIAL ARMED CORPS [CUERPO ESPECIAL ARMADO]', 'GOVERNMENT AND ARMY SECTORS', 'THE GUERRILLA ARMY OF NATIONAL LIBERATION', 'BASQUE FATHERLAND LIBERTY [ETA]', 'THE FMLN [FARABUNDO MARTI NATIONAL LIBERATION MOVEMENT]', 'THE ARMY OF NATIONAL LIBERATION', 'FAR RIGHTWING']
    containedOrganizations = []
    categories=list(organizations.keys())
    for category in categories:
        for organization in organizations[category]:
            if ((" " not in organization.strip() and organization.strip() in article.split()) or (" " in organization.strip() and (" "+organization+" ") in article)) and organization.strip() not in containedOrganizations:
                containedOrganizations.append(organization.strip())
                if category != 'MISC':
                    break
    return containedOrganizations

mlClassfier = getClassifier()


def getIncidentMachineLearning(mlClassifier,article):
    docs_test=[]
    docs_test.append(article)
    predicted = mlClassifier.predict(docs_test)
    return list(incidentTags.keys())[list(incidentTags.values()).index(predicted)]

def getVictim(article):
    tokenized_text = word_tokenize(article)
    st = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding='utf-8')
    ner_text = st.tag(tokenized_text)
    listVictims = []
    priList = ['JESUIT PRIESTS','PRIESTS','JESUIT','JESUITS']
    listOfVictims = [e for e in priList if e in article]

    if(listOfVictims.__len__()!=0):
        return [listOfVictims[0]]
    else:
        temp = 0
        lname = []
        for i, obj in enumerate(ner_text):
            if (i < temp):
                continue

            victim = []
            temp = i
            while (ner_text[temp][1] == 'PERSON'):
                victim.append(ner_text[temp][0])
                temp += 1

            if (victim.__len__() != 0 and victim.__len__()>1):
                if (" ".join(victim) not in lname):
                    lname.append(" ".join(victim[1:]))
                    listVictims.append(" ".join(victim))
        return set(listVictims)

for id in listOfIds:
    #print(id, "\n")
    incident = getIncidentMachineLearning(mlClassfier,news_dictionary[id])
    weapon = getWeapon(news_dictionary[id])

    listOfVictims = getVictim(news_dictionary[id])

    organization = getOrganization(news_dictionary[id])

    outputFile.write("ID:             " + id.upper() + "\n")
    outputFile.write("INCIDENT:       " + incident.upper() + "\n")
    outputFile.write("WEAPON:         " )


    if len(weapon) == 0:
        outputFile.write('-\n')
    else:
        for i, item in enumerate(weapon):
            if i==0:
                outputFile.write(item.upper().strip()+"\n")
            else:
                outputFile.write("                "+item.upper().strip()+"\n")
            #if i != len(weapon) - 1:
            #    outputFile.write(item.upper().strip() + '\r                ')
            #else:
            #    outputFile.write(item.upper().strip())

    outputFile.write("PERP INDIV:     -\n")

    outputFile.write("PERP ORG:       ")
    if len(organization) == 0:
        outputFile.write('-\n')
    else:
        for i, item in enumerate(organization):
            if i ==0:
                outputFile.write(item.upper().strip()+"\n")
            else:
                outputFile.write("                "+item.upper().strip()+"\n")

    outputFile.write("TARGET:         -\n")
    outputFile.write("VICTIM:         ")
    if len(listOfVictims)==0:
        outputFile.write('-\n')
    else:
        for i, item in enumerate(listOfVictims):
            if i ==0:
                outputFile.write(item.upper()+"\n")
            else:
                outputFile.write("                "+item.upper()+"\n")



    outputFile.write("\n")

outputFile.close()