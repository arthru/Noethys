#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import GestionDB
import UTILS_Dates

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

LISTE_MOIS= (_(u"Janvier"), _(u"F�vrier"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Ao�t"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"D�cembre"))

  
class Track(object):
    def __init__(self, dictValeurs={}):
        self.dictValeurs = dictValeurs
        self.MAJ()

    def MAJ(self):
        self.IDprestation = self.dictValeurs["IDprestation"]
        self.date_facturation = self.dictValeurs["date_facturation"]
        self.forfait_date_debut = self.dictValeurs["forfait_date_debut"]
        self.forfait_date_fin = self.dictValeurs["forfait_date_fin"]
        self.taux = self.dictValeurs["taux"]
        self.tarif_base = self.dictValeurs["tarif_base"]
        self.heures_facturees = self.dictValeurs["heures_facturees"]
        self.montant_mois = self.dictValeurs["montant_mois"]
        self.IDfacture = self.dictValeurs["IDfacture"]

        self.mois = self.date_facturation.month
        self.annee = self.date_facturation.year
        self.annee_mois = (self.annee, self.mois)

        self.label_prestation = u"%s %s" % (LISTE_MOIS[self.mois-1], self.annee)


# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.clsbase = kwds.pop("clsbase", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.donnees = []
        self.listeDonnees = []
        self.InitObjectListView()

    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateDDEnFr(dateDD)

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateMontant2(montant):
            if montant == None or montant == "" : return ""
            return u"%.5f %s" % (montant, SYMBOLE)

        def FormateDuree(duree):
            if duree in (None, ""):
                return ""
            else :
                return UTILS_Dates.DeltaEnStr(duree, separateur="h")

        def FormateMois(donnee):
            if donnee in ("", None):
                return ""
            else :
                annee, mois = donnee
                return u"%s %s" % (LISTE_MOIS[mois-1], annee)

        liste_Colonnes = [
            ColumnDefn(_(u"IDprestation"), "left", 0, "IDprestation", typeDonnee="entier"),
            ColumnDefn(_(u"Mois"), 'left', 100, "annee_mois", typeDonnee="texte", isSpaceFilling=True, stringConverter=FormateMois),
            ColumnDefn(_(u"Date fact."), 'center', 80, "date_facturation", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Taux"), 'center', 80, "taux", typeDonnee="montant", stringConverter=FormateMontant2),
            ColumnDefn(_(u"Tarif de base"), 'center', 80, "tarif_base", typeDonnee="montant", stringConverter=FormateMontant2),
            ColumnDefn(_(u"Heures fact."), 'center', 80, "heures_facturees", typeDonnee="entier"),
            ColumnDefn(_(u"Montant"), 'center', 80, "montant_mois", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"N� Facture"), 'center', 70, "IDfacture", typeDonnee="entier"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune mensualit�"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(1)
        
    def MAJ(self):
        self.SetObjects(self.donnees)
        self._ResizeSpaceFillingColumns() 

    def GetTracks(self):
        return self.GetObjects()

    def SetTracks(self, tracks=[]):
        self.donnees = tracks
        self.MAJ()

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualit�s"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualit�s"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des mensualit�s"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des mensualit�s"), autoriseSelections=False)


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "annee_mois" : {"mode" : "nombre", "singulier" : _(u"mensualit�"), "pluriel" : _(u"mensualit�s"), "alignement" : wx.ALIGN_CENTER},
            "heures_facturees" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},
            "montant_mois" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        ctrl = ListviewAvecFooter(panel, kwargs={})
        listview = ctrl.GetListview()
        listview.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(ctrl, 1, wx.ALL|wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
