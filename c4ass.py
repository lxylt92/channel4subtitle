import xml.etree.ElementTree as ET
import os
import sys
import re
import fileinput


def sync2time(ms_str):
    # milliseconds to ass time format
    ms = int(ms_str)
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return ("%02d:%02d:%02d.%03d" % (h, m, s, ms))


def color2ass(color):
    # convert plain text color name to ass subtitle code
    # color:white;  cyan  yellow  white  #11FF11
    # ass color {\c&H1A15F9&}
    ass = ''
    color = color[6:len(color) - 1]
    if color[0:1] == '#':
        ass = ['{\\c&H' + color[5:7] + color[3:5] + color[1:3] + '&}',
               's' + color[5:7] + color[3:5] + color[1:3]]
    elif color == 'white':
        ass = ['{\\c&HFFFFFF&}', 'white']
    elif color == 'yellow':
        ass = ['{\\c&H00FFFF&}', 'yellow']
    elif color == 'cyan':
        ass = ['{\\c&HFFFF00&}', 'cyan']
    elif color == 'red':
        ass = ['{\\c&H0000FF&}', 'red']
    elif color == 'blue':
        ass = ['{\\c&HFF0000&}', 'blue']
    elif color == 'pink':
        ass = ['{\\c&HFF00FF&}', 'pink']
    elif color == 'green':
        ass = ['{\\c&H00FF00&}', 'green']
    elif color == 'orange':
        ass = ['{\\c&H007FFF&}', 'orange']
    return ass


def endtime(sublist_input):
    # add next line start time as previous line end time
    sublist = sublist_input
    print str(len(sublist)) + ' lines loaded.'
    lines_empty = list()
    end = ''
    for i, lines in enumerate(reversed(sublist)):
        # find empty lines
        lines[1] = end
        end = lines[0]
        if lines[3] == '':
            lines_empty.append(len(sublist) - i - 1)
    for i, lines in enumerate(lines_empty):
        # delete empty lines
        del sublist[lines]
    print str(len(lines_empty)) + ' empty lines deleted.'
    print str(len(sublist)) + ' lines left.'
    return sublist

file = open(sys.argv[1])

plainlines = ''

while 1:
    # replace invalid <br> for <br />
    lines = file.readlines(100000)
    if not lines:
        break
    for i, line in enumerate(lines):
        plainlines = plainlines + line.replace('<br>', '<br />')
    break
tree = ET.fromstring(plainlines)

title = tree.find('Body')
subtitles_list = list()
for Sync in title.iter(tag='Sync'):
    subtitle_list = ['', '', '', '']
    #start, end, style, content
    # start time
    start = Sync.get("Start")
    subtitle_list[0] = sync2time(start)
    # content
    flag = 0
    str_tmp = ''
    style = ['{\\c&HFFFFFF&}', 'Default']
    for span in Sync.find('P').findall('span'):
        # remove doube spaces
        content = re.sub(' +', ' ', span.text)
        if content[:1] == ' ':
            content = content[1:]
        if flag == 0:
            str_tmp = str_tmp + content
            style = color2ass(span.get('style'))
        else:
            str_tmp = str_tmp + '\\n' + \
                color2ass(span.get('style'))[0] + content
        flag = flag + 1
    subtitle_list[2] = style
    subtitle_list[3] = str_tmp
    subtitles_list.append(subtitle_list)
subtitles_final = endtime(subtitles_list)

# output to ass file
ass_output = list()
ass_output.append('[Script Info]')
ass_output.append('; Script generated by c4ass 0.1')
ass_output.append('; http://sofronio.cn/')
ass_output.append('Title: ' + sys.argv[1])
ass_output.append('ScriptType: v4.00+')
ass_output.append('PlayDepth: 0')
ass_output.append('YCbCr Matrix: TV.601')
ass_output.append('PlayResX: 1280')
ass_output.append('PlayResY: 720')
ass_output.append('')
ass_output.append('[V4+ Styles]')
ass_output.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding')
ass_output.append(
    'Style: Default,Arial,32,&H00FFFFFF,&H0300FFFF,&H00000000,&H02000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1')
ass_output.append(
    'Style: white,Arial,32,&H00FFFFFF,&H0300FFFF,&H00000000,&H02000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1')
ass_output.append(
    'Style: yellow,Arial,32,&H0000FFFF,&H0300FFFF,&H00000000,&H02000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1')
ass_output.append(
    'Style: cyan,Arial,32,&H00FFFF00,&H0300FFFF,&H00000000,&H02000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1')
ass_output.append('')
ass_output.append('[Events]')
ass_output.append(
    'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
for i, lines in enumerate(subtitles_final):
    ass_output.append(
        'Dialogue: 0,' + lines[0] + ',' + lines[1] + ',' + lines[2][1] + ',,0,0,0,,' + lines[3])
# add \r\n for notepade.exe new line support
for i, lines in enumerate(ass_output):
    ass_output[i] = lines + '\r\n'

output = open(sys.argv[1] + '.ass', 'w+b')
output.writelines(ass_output)
output.close()
print 'Process complete. ASS Subtitle output: ' + sys.argv[1] + '.ass'
