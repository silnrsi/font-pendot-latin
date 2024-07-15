#!/usr/bin/python3

import xml.etree.ElementTree as ET
import fontParts.world as fontparts
import csv
import argparse


def main():
    parser = argparse.ArgumentParser(description='Prepare Pendot glyph names')
    parser.add_argument('glyphsapp', help='Glyphs.app GlyphData.xml file')
    parser.add_argument('cdga', help='CDGA glyphs_data.csv file')
    parser.add_argument('pendot', help='Pendot glyphs_data.csv file')
    args = parser.parse_args()

    gd_cdga, fieldnames = read_csv(args.cdga)
    glyphsapp = read_xml(args.glyphsapp)
    gd_pendot = []
    for glyph in gd_cdga:
        temp_usv = glyphsapp_name = ''
        if glyph['ps_name'] in glyphsapp:
            temp_usv = glyphsapp[glyph['ps_name']]['usv']
            glyphsapp_name = glyphsapp[glyph['ps_name']]['name']
        glyph['temp_usv'] = temp_usv
        glyph['glyphsapp_name'] = glyphsapp_name
        gd_pendot.append(glyph)
    fieldnames.extend(['temp_usv', 'glyphsapp_name'])
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


def read_xml(filename):
    data = dict()
    tree = ET.parse(filename)
    root = tree.getroot()
    for record in root:
        production = name = record.attrib['name']
        if 'production' in record.attrib:
            production = record.attrib['production']
        if 'unicode' in record.attrib:
            usv = record.attrib['unicode']
            # codepoint = int(usv, 16)
        else:
            usv = ''
            # codepoint = -1
        glyph = {}
        glyph['name'] = name
        # glyph['production'] = production
        glyph['usv'] = usv
        data[production] = glyph
    return data


if __name__ == '__main__':
    main()
