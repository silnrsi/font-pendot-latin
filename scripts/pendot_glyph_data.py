#!/usr/bin/python3

import xml.etree.ElementTree as ET
import fontParts.world as fontparts
import csv
import argparse


def main():
    parser = argparse.ArgumentParser(description='Prepare Pendot glyph names')
    parser.add_argument('glyphsapp', help='Glyphs.app GlyphData.xml file')
    parser.add_argument('ufo', help='CDGA UFO')
    parser.add_argument('cdga', help='CDGA glyphs_data.csv file')
    parser.add_argument('pendot', help='Pendot glyphs_data.csv file')
    parser.add_argument('custom', help='Custom name mapping csv file')
    args = parser.parse_args()

    base_data, ufo_data = read_ufo(args.ufo)
    gd_cdga, fieldnames = read_csv(args.cdga)
    custom_names = read_csv2dict(args.custom)
    glyphsapp_codepoint, glyphsapp_production = read_xml(args.glyphsapp)
    gd_pendot = []
    used_glyphsapp_names = []
    for glyph in gd_cdga:
        ufo_codepoint = temp_usv = glyphsapp_name = ''
        to_review = []

        glyph_name = glyph['glyph_name']

        # grab unicode for glyph from ufo
        if glyph_name in ufo_data:
            if ufo_data[glyph_name] != -1:
                ufo_codepoint = str.upper(hex(ufo_data[glyph_name]))[2:7].zfill(4)
        else:
            to_review.append('NotInUfo')

        # find codepoint to be used for looking up character information
        if glyph_name in base_data:
            base_codepoint = base_data[glyph_name]
        else:
            base_codepoint = -1
            #to_review.append('NotInUfo')
        base_glyph_name, dot_glyph_name, suffix_glyph_name = glyph_name.partition('.')

        # find production name to be used for looking up character information
        production = glyph['ps_name']
        base_production, dot_production, suffix_production = production.partition('.')

        # verify the suffixes are the same
        if suffix_glyph_name != suffix_production:
            to_review.append('SuffixMismatch')

        if base_codepoint in glyphsapp_codepoint:
            # lookup data in the Glyphs.app GlyphData.xml file by codepoint
            temp_usv = glyphsapp_codepoint[base_codepoint]['usv']
            glyphsapp_name = glyphsapp_codepoint[base_codepoint]['name']
            if suffix_glyph_name:
                temp_usv = ''
                glyphsapp_name = f'{glyphsapp_name}{dot_glyph_name}{suffix_glyph_name}'
        elif base_production in glyphsapp_production:
            # lookup data in the Glyphs.app GlyphData.xml file by base production name
            temp_usv = glyphsapp_production[base_production]['usv']
            glyphsapp_name = glyphsapp_production[base_production]['name']
            if suffix_production:
                temp_usv = ''
                glyphsapp_name = f'{glyphsapp_name}{dot_production}{suffix_production}'
        elif base_glyph_name in custom_names:
            glyphsapp_name = custom_names[base_glyph_name]
            if suffix_glyph_name:
                temp_usv = ''
                glyphsapp_name = f'{glyphsapp_name}{dot_glyph_name}{suffix_glyph_name}'            
            to_review.append('CustomName')
            # print(glyph_name, glyphsapp_name)
        elif glyph_name[len(glyph_name)-3:] == "Dep":
            to_review.append('Deprecated')
        elif glyph_name in ('.notdef', '.null', 'nonmarkingreturn'):
            # first three glyph names are special
            glyphsapp_name = glyph_name
        else:
            to_review.append('NotInGAorCN')

        # check for mismatched USVs
        # if temp_usv != "" and temp_usv != ufo_codepoint:
            # print("usv mismatch", glyph_name, "temp_usv", temp_usv, "UFO", ufo_codepoint)

        # test for missing or duplicate glyphsapp_names        
        if glyphsapp_name == "":
            print("%s has no glyphsapp_name" % glyph_name)
        elif glyphsapp_name in used_glyphsapp_names:
            print("Name %s already in use" % glyphsapp_name)
        else:
            used_glyphsapp_names.append(glyphsapp_name)

        glyph['usv'] = ufo_codepoint
        glyph['glyphsapp_name'] = glyphsapp_name
        glyph['to_review'] = ' '.join(to_review)
        gd_pendot.append(glyph)
    fieldnames.extend(['usv', 'glyphsapp_name', 'to_review'])
    write_csv(gd_pendot, fieldnames, args.pendot)


def read_csv(filename):
    data = []
    with open(filename, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames
        for row in reader:
            data.append(row)
    return data, fieldnames


def read_csv2dict(filename):
    namedict = {}
    with open(filename, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            namedict[row['silname']] = row['newname']
    # print(namedict)
    return namedict


def write_csv(gd, fieldnames, filename):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in gd:
            writer.writerow(row)


def read_ufo(filename):
    base_data = dict()
    ufo_data = dict()
    rev_cmap = dict()
    font = fontparts.OpenFont(filename)

    # create the reverse cmap
    for glyph in font:
        if glyph.unicode:
            base_glyph_name, dot, suffix = glyph.name.partition('.')
            rev_cmap[base_glyph_name] = glyph.unicode

    # read data from the UFO
    for glyph in font:
        base_glyph_name, dot, suffix = glyph.name.partition('.')

        if base_glyph_name in rev_cmap:
            basepoint = rev_cmap[base_glyph_name]
        else:
            basepoint = -1
        base_data[glyph.name] = basepoint

        if glyph.unicode:
            ufopoint = glyph.unicode
        else:
            ufopoint = -1
        ufo_data[glyph.name] = ufopoint

    return base_data, ufo_data


def read_xml(filename):
    data_codepoint = data_production = dict()
    tree = ET.parse(filename)
    root = tree.getroot()
    for record in root:
        if 'unicode' in record.attrib:
            usv = record.attrib['unicode']
            codepoint = int(usv, 16)
            production = name = record.attrib['name']
            if 'production' in record.attrib:
                production = record.attrib['production']
            glyph = {}
            glyph['name'] = name
            glyph['usv'] = usv
            data_codepoint[codepoint] = glyph
            data_production[production] = glyph
    return data_codepoint, data_production


if __name__ == '__main__':
    main()
