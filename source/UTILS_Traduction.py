#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import shelve
import os
import re

DICT_TRADUCTIONS = None

def ChargeTraduction(nom=""):
    """ Charge un fichier de langage """
    global DICT_TRADUCTIONS
    dictTraductions = {}
    
    # Recherche le fichier de langage par d�faut ".lang" puis un �ventuel fichier perso ".xlang"
    for extension in ("lang", "xlang") :
        nomFichier = "Lang/%s.%s" % (nom, extension)
        if os.path.isfile(nomFichier) :
            fichier = shelve.open(nomFichier, "r")
            for key, valeur in fichier.iteritems() :
                key = key.decode("iso-8859-15")
                dictTraductions[key] = valeur
            fichier.close()
            
    # M�morise les traductions
    DICT_TRADUCTIONS = dictTraductions
    
    
    
def _(chaine) :
    """ Traduit une cha�ne """
    # Recherche si une traduction existe
    if DICT_TRADUCTIONS != None :
        if DICT_TRADUCTIONS.has_key(chaine) :
            return DICT_TRADUCTIONS[chaine]
    
    # Sinon renvoie la chaine par d�faut
    return chaine


def CreationFichierTest():
    nomFichier = "Lang/anglais.xlang"
    if os.path.isfile(nomFichier) :
        flag = "w"
    else :
        flag = "n"
    fichier = shelve.open(nomFichier, flag)
    fichier["##NOM_LANGUE"] = u"Anglais"
    fichier["##CODE_LANGUE"] = "anglais"
    fichier["##TRADUCTEUR_NOM"] = u"DUPOND"
    fichier["##TRADUCTEUR_PRENOM"] = u"C�lestin"
    fichier["R�gler une facture"] = u"R�gler une facture2"
    fichier["  Liste  "] = u"  LISTE!!!  "
    fichier["Badgeage"] = u"BadgetrucPERSO"
    
    fichier.close()


def GenerationFichierTextes() :
    listeFichiers = os.listdir(os.getcwd())
    listeFichiersTrouves = []
    dictTextes = {}
    
    # Recherche des textes
    exp = re.compile(r"_\(u\".*?\"\)")
    
    for nomFichier in listeFichiers :
    
            if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False and nomFichier not in ("CreateurMAJ.py", "CreateurANNONCES.py") :
                # Ouverture du fichier
                fichier = open(nomFichier, "r")
                texte = "\n".join(fichier.readlines())
                fichier.close() 
                
                # Analyse du fichier
                listeChaines = re.findall(exp, texte)
                for chaine in listeChaines :      
                    chaine = chaine [4:-2]
                                  
                    valide = False
                    for caract in "abceghijklmopqrtvwxyz" :
                        if caract in chaine.lower() :
                            valide = True
                    if len(chaine) < 2 :
                        valide = False
                    if "Images/" in chaine :
                        valide = False
                    
                    if valide == True :
                        if dictTextes.has_key(chaine) == False :
                            dictTextes[chaine] = []
                        dictTextes[chaine].append(nomFichier)
    
    # G�n�ration du fichier Shelve
    nomFichier = "Textes.dat"
    if os.path.isfile(nomFichier) :
        flag = "w"
    else :
        flag = "n"
    fichier = shelve.open(nomFichier, flag)
    for texte, listeFichiers in dictTextes.iteritems() :
        fichier[texte] = listeFichiers
    fichier.close()
    print "Generation du fichier de textes terminee."




if __name__ == "__main__":
    GenerationFichierTextes() 
    
