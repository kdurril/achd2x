#!/usr/bin/jython
# target: -Dpython.path=/Development/pdfbox-2.0.0-RC2/app/target/pdfbox-app-2.0.0-RC2.jar
# -*- coding: utf-8 -*-
#
# Parse ACHD PDF from 2014-03-01 to present
# this accounts for grid structure of Food Safety Assessment
# return the document as a json document

import org.apache.pdfbox.pdmodel
import org.apache.pdfbox.text
import org.apache.pdfbox.cos
import org.apache.pdfbox.text.TextPosition as TextPosition

import java.awt.Rectangle
import java.awt.geom.Rectangle2D.Float as r2df
import itertools
import codecs
import glob
import os
import re
import json
from collections import OrderedDict
#import csv

class achdInspect(object):
    "open file, create region boxes, extract text from regions, export"
    def __init__(self, filename):
        self.filename=filename
        with open(filename, "rb") as opendfile:
            self.f = opendfile.read()
        self.base = org.apache.pdfbox.pdmodel
        self.doc = self.base.PDDocument.load(self.f)
        self.page = self.doc.getPages()
        self.count = self.doc.numberOfPages
        
        #basic extract all text
        self.w = org.apache.pdfbox.text.PDFTextStripper()
        self.base_text = self.w.getText(self.doc)

        #define areas for extraction
        self.wz = org.apache.pdfbox.text.PDFTextStripperByArea()
        #self.wz.extractRegions(self.doc.getPage(0))
        self.strip = org.apache.pdfbox.text.PDFTextStripperByArea()
        self.base_all = (self.strip.extractRegions(self.doc.getPage(x)) for x in range(self.count))
        #self.region_chain = self.chain_regions()

    class regionBox(object):
        "make regions from java rectangles"
        def __init__(self, label, boxinit, boxcount):
            self.label = label
            self.boxinit = boxinit
            self.boxcount = boxcount
            self.box = list(self.rect_list())

        def rect(self, re_list):
            "convert tuple to rectangle object" 
            self.r_angle = r2df(*re_list)
            return self.r_angle
        
        def rect_list(self):
            "create tuples for region"
            #x,y,w,h
            #send boxcount as a tuple, so it can unpack
            for x in range(*self.boxcount):
                yield {"label": self.label+str(x),
                       "box": self.rect(
                        (self.boxinit[0],
                        self.boxinit[1]+(x*self.boxinit[3]), 
                        self.boxinit[2], 
                        self.boxinit[3]))
                        }
    
    #Regions and pages should be inputs for the extraction
    #Chain Regions, get_regions, getAllText should have inputs

    #What is the longest sequence that matches this pattern ((\d+)\n){33,}?
    #This can be the input for range in the regionBox of make_regions
    #PDFTextStripper treats the full sequence as a single media box
    #I would like to pull media boxes individually
    #Specific first, generalize later

    def make_regions(self):
        "Food Safety Assessment Categories page 1"
        self.tag = self.regionBox("tag", (62, 230, 419, 13.5), (26,))
        self.diamond = self.regionBox("diamond", (346, 230, 26, 13.5), (26,))
        self.satisfactory = self.regionBox("satisfactory", (373, 230, 26, 13.5), (26,))
        self.not_observed = self.regionBox("not_observed", (401, 230, 26, 13.5), (26,))
        self.not_applicable = self.regionBox("not_applicable", (427, 230, 26, 13.5), (26,))
        self.violation = self.regionBox("violation", (455, 230, 26, 13.5), (26,))
        self.high = self.regionBox("high", (486, 230, 26, 13.5), (26,))
        self.med = self.regionBox("med", (513, 230, 26, 13.5), (26,))
        self.low  = self.regionBox("low", (544, 230, 26, 13.5), (26,))
        
        self.clientinfo_a = self.regionBox("client_a",(35, 104, 205, 13.5), (6,))
        self.clientinfo_b = self.regionBox("client_b",(240, 104, 205, 13.5), (6,))
        self.clientinfo_c = self.regionBox("client_c",(410, 104, 190, 13.5), (6,))
        
        self.regions = (self.tag,
                self.diamond,
                self.satisfactory,
                self.not_observed,
                self.not_applicable,
                self.violation,
                self.high,
                self.med,
                self.low,
                self.clientinfo_a,
                self.clientinfo_b,
                self.clientinfo_c
                )
        return self.regions

    def more_regions(self):
        "General Sanitation Section page 1"
        self.tag = self.regionBox("tag-san", (62, 612, 180, 13.5), (10,))
        self.diamond = self.regionBox("diamond-san", (346, 612, 26, 13.5), (10,))
        self.satisfactory = self.regionBox("satisfactory-san", (373, 612, 26, 13.5), (10,))
        self.not_observed = self.regionBox("not_observed-san", (401, 612, 26, 13.5), (10,))
        self.not_applicable = self.regionBox("not_applicable-san", (427, 612, 26, 13.5), (10,))
        self.violation = self.regionBox("violation-san", (455, 612, 26, 13.5), (10,))
        self.high = self.regionBox("high-san", (486, 612, 26, 13.5), (10,))
        self.med = self.regionBox("med-san", (513, 612, 26, 13.5), (10,))
        self.low  = self.regionBox("low-san", (544, 612, 26, 13.5), (10,))
        self.regions = (self.tag, 
                self.diamond, 
                self.satisfactory, 
                self.not_observed, 
                self.not_applicable, 
                self.violation, 
                self.high, 
                self.med, 
                self.low)
        return self.regions

    def make_p2_regions(self):
        "Inspection Details from page 2"
        self.info_a = self.regionBox("inspect_a",(36, 117, 275, 13.5), (3,))
        self.info_b = self.regionBox("inspect_b",(328, 117, 115, 13.5), (3,))
        self.info_c = self.regionBox("inspect_c",(444, 117, 115, 13.5), (3,))
        self.clientinfo_a = self.regionBox("comments_a",(36, 162, 540, 12.5), (50,))
        self.regions = (
                self.info_a,
                self.info_b,
                self.info_c,
                self.clientinfo_a)
        return self.regions

    def make_page_comments(self,page_num):
        "Violation Comments from page 2"
        label = "comment"+"_p"+str(page_num)+"_"
        self.clientinfo_a = self.regionBox(label,(36, 105, 540, 12.5), (50,))
        
        self.regions = (self.clientinfo_a,)
                
        return self.regions

    #
    #Gather region information 
    #
    def chain_regions(self, *args):
        "Collection of regions"
        #args are iterable
        new_container = []
        iter_chain = itertools.chain.from_iterable(args)
        for x in iter_chain:
            if x.box:
                new_container.extend(x.box)
        self.region_chain = new_container
        return self.region_chain  

    def set_regions(self):
        "for the TextByArea object, add regions"
        #region_chain = self.chain_regions()
        for x in self.region_chain:
            self.wz.addRegion(x["label"], x["box"])

    def get_all_text(self, page_num=0, stripper=None):
        "Retrieved text from regions"
        #doc - fixed
        #page - input
        #stripper - input i.e. wz.extractRegions should be input
        new_container = []
        doc_page = self.doc.getPage(page_num)
        self.wz.extractRegions(doc_page)
        for x in self.wz.getRegions():
            new_container.append((x, self.wz.getTextForRegion(x)))
        return new_container

    def get_all_text_alt(self, page_num=0, stripper=None):
        "Generator retrieved text from regions"
        #doc - fixed
        #page - input
        #stripper - input i.e. wz.extractRegions should be input
        doc_page = self.doc.getPage(page_num)
        self.wz.extractRegions(doc_page)
        for x in self.wz.getRegions():
            yield (x, self.wz.getTextForRegion(x))

    def text_output(self):
        #doc, wz textstripperbyarea, and area are the objects
        self.region_chain = self.chain_regions(self.make_regions(), 
                                               self.more_regions())
        self.set_regions()
        self.wz.extractRegions(self.doc.getPage(0))
        return self.get_all_text(page_num=0, stripper=None)

    def text_output_more(self):
        #doc, wz textstripperbyarea, and area are the objects
        self.region_chain = self.chain_regions(self.make_p2_regions())
        self.set_regions()
        self.wz.extractRegions(self.doc.getPage(1))
        return self.get_all_text(page_num=1, stripper=None)

    def text_generalized(self, page_num, *args):
        #doc, wz textstripperbyarea, and area are the objects
        self.region_chain = self.chain_regions(*args)
        self.set_regions()
        self.wz.extractRegions(self.doc.getPage(page_num))
        return self.get_all_text(page_num=page_num, stripper=None)

    def text_generalized_alt(self, page_num, *args):
        #doc, wz textstripperbyarea, and area are the objects
        self.region_chain = self.chain_regions(*args)
        new_container = []
        doc_page = self.doc.getPage(page_num)
        stripper = org.apache.pdfbox.text.PDFTextStripperByArea()
        #set regions
        for x in self.region_chain:
            stripper.addRegion(x["label"], x["box"])
        
        stripper.extractRegions(doc_page)

        for y in stripper.getRegions():
            new_container.append((y, stripper.getTextForRegion(y)))
        return new_container

    def doc_label(self):
        "gather the labeled data from each page"
        new_container = []
        for x in range(self.count):
            if x >= 2:
                pX = self.text_generalized_alt(x,self.make_page_comments(x))
                new_container.extend(pX)
            elif x == 1:
                p1 = self.text_generalized_alt(x,self.make_p2_regions())
                new_container.extend(p1)
            elif x == 0:
                p0 = self.text_generalized_alt(x,self.make_regions(),self.more_regions())
                new_container.extend(p0)
        return new_container

    def doc_label_ALT(self):
        "gather the labeled data from each page"
        
        for x in range(self.count):
            if x >= 2:
                pX = self.text_generalized_alt(x,self.make_page_comments(x))
                for attribute in pX:
                    if attribute[1] != '\n':
                        yield attribute
            elif x == 1:
                p1 = self.text_generalized_alt(x,self.make_p2_regions())
                for attribute in p1:
                    if attribute[1] != '\n':
                        yield attribute
            elif x == 0:
                p0 = self.text_generalized_alt(x,self.make_regions(),self.more_regions())
                for attribute in p0:
                    if attribute[1] != '\n':
                        yield attribute

    def category_count(self):
        pattern = re.compile("(\d+\n){25,}")
        category = re.search(pattern,self.base_text)
        return max(int(x) for x in category.group(0).split("\n") if x !="")

    def jsonify(self):
        ".get_all_text(page_number=0, stripper=None)"
        with open(os.path.basename(self.filename)[:-4]+'.json', 'a') as achd_out:
            achd_out.write(json.dumps(OrderedDict(self.doc_label())))

def jsonify(filename, serial):
    ".get_all_text(page_number=0, stripper=None)"
    with codecs.open(filename, 'w', 'utf-8') as achd_out:
        achd_out.write(json.dumps(OrderedDict(serial)))

def base_text(filename, serial):
    ".get_all_text(page_number=0, stripper=None)"
    with codecs.open(filename, 'w', 'utf-8') as achd_out:
        achd_out.write(serial.base_text)

