import sys
import os



COMMAND_PEN_DOWN = "M3 S31 (Pen down)\nG4 P0.25 (wait)"
COMMAND_PEN_UP = "M3 S90 (Pen up)\nG4 P0.25 (wait)"

if len(sys.argv) < 2:
    sys.stderr.write("Error: missing filename. \nUsage: " + os.path.basename(sys.argv[0]) + " filename.ext\n")
    sys.exit(-1)

infilename = sys.argv[1]
file = []
with open (infilename) as infile:
    for fileline in infile:
        if fileline[0].upper() not in 'M%': #remove initial M-commands
            file.append(fileline.rstrip())

newfile = []
newfile.append('%\n')
pen_down = False;
for fileline in file:
    words = fileline.split()
    newwords = []
    if len(words)>0 and words[0][0] == 'G' and int(words[0][1:]) <= 9: # its a gcode motion line
        for word in words:
            if word[0].upper() == 'Z':
                pen_cmd_down = (float(word[1:]) <= 0.0)
                if pen_cmd_down != pen_down:
                    newfile.append(COMMAND_PEN_DOWN if pen_cmd_down else COMMAND_PEN_UP)
                    pen_down = pen_cmd_down
            else :
                newwords.append(word)
        if len(newwords) > 2 or (len(newwords) > 1 and newwords[1][0] != 'F'): # get rid of empty feed command
            newfile.append(" ".join(newwords))
    else:
        newfile.append(fileline)

newfile.append('(M5 fake stop spindle)')            
newfile.append('%')


with open (os.path.splitext(infilename)[0] + ".eggbot.gcode", 'w') as outfile:
    outfile.write('\n'.join(newfile))
