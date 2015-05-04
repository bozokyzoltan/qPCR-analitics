#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky on 2015.04.17.
Under GPL licence.

"""

import qpcrdata
import label
import numpy as np
import excel
import wx

class FrontEnd(wx.Frame):
    """
    """
    def __init__(self):
        """
        """

        wx.Frame.__init__(self, None, wx.ID_ANY, "qPCR",
                          size = (300, 300), style = wx.CAPTION | wx.MINIMIZE_BOX |wx.CLOSE_BOX)
        self.Centre()
        #
        self.panel1 = wx.Panel(self, wx.ID_ANY, size =(300,300))

        # ---------------------
        # 1. Load datafile
        # ---------------------
        self.button_data = wx.Button(self.panel1, id=wx.ID_ANY, label="1. Load datafile", pos=(5,5), size=(150,30))
        self.button_data.Bind(wx.EVT_BUTTON, self.onButton_data)
        # ---------------------
        # 2. Load labels
        # ---------------------
        self.button_label = wx.Button(self.panel1, id=wx.ID_ANY, label="2. Load label file", pos=(5,35), size=(150,30))
        self.button_label.Bind(wx.EVT_BUTTON, self.onButton_label)
        self.button_label.Hide()
        # ---------------------
        # 3. Save data
        # ---------------------
        self.button_save = wx.Button(self.panel1, id=wx.ID_ANY, label="3. Save converted data", pos=(5,65), size=(150,30))
        self.button_save.Bind(wx.EVT_BUTTON, self.onButton_save)
        self.button_save.Hide()
        #
        wx.StaticText(self.panel1, id=wx.ID_ANY, pos=(255,0), label='bozoky')
        #
        return None
    ### ========================================================================
    def onButton_data(self, event):
        """
        This method is fired when its corresponding button is pressed
        """
        openFileDialog = wx.FileDialog(self,
                               'Open plate reader measurement file in plate format',
                               '',
                               '',
                               'Plate reader files (*.xlsx)|*.xlsx',
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                      )
        #
        if openFileDialog.ShowModal() != wx.ID_CANCEL:
            #
            self.data_filename = openFileDialog.GetPath()

            self.data = qpcrdata.Data()
            self.data.read_datafile(self.data_filename)


            #
            self.save_filename = openFileDialog.GetPath().split('.')[0] + '_analyzed.xls'
            #
            self.button_label.Show()
        #
        openFileDialog.Destroy()
        #
        return None
    ### ========================================================================
    def onButton_label(self, event):
        """
        This method is fired when its corresponding button is pressed
        """
        openFileDialog = wx.FileDialog(self,
                               'Open plate reader measurement file in plate format',
                               '',
                               '',
                               'Plate reader files (*.xlsx)|*.xlsx',
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                      )
        #
        if openFileDialog.ShowModal() != wx.ID_CANCEL:
            #
            self.nametag = label.Label()
            self.nametag.read_label_file(openFileDialog.GetPath())
            #
            if len(self.nametag.label_types) > 1:
                self.test_tags = []
                self.control_tags = []
                test_label = wx.StaticText(self.panel1, -1, 'Test gene:', pos=(25, 100))
                control_label = wx.StaticText(self.panel1, -1, 'Control gene:', pos=(125, 100))
                for j, tag in enumerate(self.nametag.label_types[1]):
                    self.test_tags.append(wx.RadioButton(self.panel1, -1, tag, pos=( 25,120+j*20), style=wx.RB_GROUP))
                    self.control_tags.append(wx.RadioButton(self.panel1, -1, tag, pos=(125,120+j*20)))
                    for control_gene in ['GAPDH', 'GUSB', 'CFTR']:
                        if control_gene in tag.upper():
                            self.control_tags[-1].SetValue(True)
            #
            self.button_save.Show()
        #
        openFileDialog.Destroy()
        #
        return None
    ### ========================================================================
    def onButton_save(self, event):
        """
        This method is fired when its corresponding button is pressed
        """
        if self.save_filename != '':

            values = {}
            for well in self.nametag.order:
                if '+' in ''.join(self.nametag.all_labels[well]):
                    name = ' '.join(self.nametag.all_labels[well])#[:2])
                    if name not in values:
                        values[name] = {'well' : [], 'value': []}
                    values[name]['well'].append(str(well))
                    if self.data.data[well][-1] != 'No Ct':
                        values[name]['value'].append(self.data.data[well][-1])

            gene_data = {}
            for gene in self.nametag.label_types[1]:
                ko = {}
                wt = []
                for name in values:
                    if gene in name.split()[0]:
                        if values[name]['well'][0] in self.nametag.control:
                            for value in values[name]['value']:
                                wt.append(value)
                        else:
                            if len(values[name]['value']) > 0:
                                ko[name] = np.array(values[name]['value']).mean()
                            else:
                                ko[name] = 0.0
                if len(wt) > 0:
                    wt = np.array(wt).mean()
                else:
                    wt = 0.0
                for mouse in ko:
                    ko[mouse] -= wt
                gene_data[gene] = ko
                
            analyzed = [['test gene', 'control gene', 'mouse', 'value', '', 'test KO-WT','control KO-WT','test - control']]

            for i, test in enumerate(self.test_tags):
                if test.GetValue():
                    gene = self.nametag.label_types[1][i]
                    control_genes = []
                    for j, tag in enumerate(self.control_tags):
                        if tag.GetValue():
                            control_genes.append(self.nametag.label_types[1][j])
                    for cgene in control_genes:
                        for ko in gene_data[gene]:
                            for co in gene_data[cgene]:
                                if ko.split()[1:] == co.split()[1:]:
                                    score = 2**(gene_data[cgene][co] - gene_data[gene][ko])
                                    analyzed.append([gene,
                                                     cgene,
                                                     ' '.join(ko.split()[1:]) ,
                                                     score,
                                                     '',
                                                     gene_data[gene][ko], 
                                                     gene_data[cgene][co],
                                                     gene_data[gene][ko] - gene_data[cgene][co]
                                                   ])

            analyzed = np.array(analyzed)
            analyzed = analyzed.T

            groups_threshold = [['Threshold', self.data.data[self.data.data.keys()[0]][2]],['']]
            for i, block in enumerate(self.nametag.label_types):
                group = ['group '+ str(i)]
                for unique_name in self.nametag.label_types[block]:
                    group.append(unique_name)
                groups_threshold.append(group)


            keys = values.keys()
            keys.sort()

            output_data = [['Name', 'Mean', 'Std', 'N']]

            for name in keys:
                a = np.array(values[name]['value'])

                well_info = []
                well_info.append(name)
                if len(a) > 0:
                    well_info.append(a.mean())
                    well_info.append(a.std())
                else:
                    well_info.append('')
                    well_info.append('')
                well_info.append(len(a))
                well_info.append('')
                for well in values[name]['well']:
                    well_info.append(well)
                for value in a:
                    well_info.append(value)

                output_data.append(well_info)

            output_data = np.array(output_data)
            output_data = output_data.T
            output = excel.Excel()
            
            output.add_sheet('result', analyzed)
            output.add_sheet('qPCR', output_data)
            output.add_sheet('info', groups_threshold)
            
            output.save_excel_file(self.save_filename)
            print self.save_filename, 'saved!'
            #
            self.button_save.Label = '4. Saved'
        #
        return None
    ### ========================================================================
    ### ========================================================================
    ### ========================================================================
