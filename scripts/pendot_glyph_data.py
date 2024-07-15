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
    args = parser.parse_args()

    ufo_data = read_ufo(args.ufo)
    gd_cdga, fieldnames = read_csv(args.cdga)
    glyphsapp_codepoint, glyphsapp_production = read_xml(args.glyphsapp)
    gd_pendot = []
    for glyph in gd_cdga:
        temp_usv = glyphsapp_name = ''
        to_review = []

        # find codepoint to be used for looking up character information
        glyph_name = glyph['glyph_name']
        if glyph_name in ufo_data:
            base_codepoint = ufo_data[glyph_name]
        else:
            base_codepoint = -1
            to_review.append('NotInUfo')
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
        elif glyph_name in ('.notdef', '.null', 'nonmarkingreturn'):
            # first three glyph names are special
            glyphsapp_name = glyph_name
        else:
            to_review.append('NotInGlyphsApp')
        glyph['temp_usv'] = temp_usv
        glyph['glyphsapp_name'] = glyphsapp_name
        glyph['to_review'] = ' '.join(to_review)
        gd_pendot.append(glyph)
    fieldnames.extend(['temp_usv', 'glyphsapp_name', 'to_review'])
    write_csv(gd_pendot, fieldnames, args.pendot)


def read_csv(filename):
    gd = []
    with open(filename, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames
        for row in reader:
            gd.append(row)
    return gd, fieldnames


def write_csv(gd, fieldnames, filename):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in gd:
            writer.writerow(row)


def read_ufo(filename):
    data = dict()
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
            codepoint = rev_cmap[base_glyph_name]
        else:
            codepoint = -1
        # data[glyph.name] = (codepoint, glyph.name, '(UFO)')
        data[glyph.name] = codepoint

    return data


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
            glyph['production'] = production
            glyph['usv'] = usv
            data_codepoint[codepoint] = glyph
            data_production[production] = glyph
    return data_codepoint, data_production


if __name__ == '__main__':
    main()
