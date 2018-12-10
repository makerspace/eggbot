import sys
import os
import argparse

COMMAND_PEN_DOWN = "M3 S31 (Pen down)\nG4 P0.25 (wait)"
COMMAND_PEN_UP = "M3 S90 (Pen up)\nG4 P0.25 (wait)"

def main():
    parser = argparse.ArgumentParser(description="Converts gcode files from inkscape to be used by the eggbot (e.g. removes z-movements)")
    parser.add_argument("filename", help="The .gcode file to convert to eggbot compatible gcode")
    parser.add_argument("--force", "-f", action="store_true", help="Force usage of input file even if wrong extension, and output file even if it will be overwritten.")
    ns = parser.parse_args()

    # Get passed arguments
    infile_path = ns.filename
    force = ns.force

    infile_basename, infile_extension = os.path.splitext(infile_path)

    # Check output file and force status
    outfile_path = infile_basename + ".eggbot" + infile_extension
    output_exists = os.path.isfile(outfile_path)
    if output_exists and force:
        print("The output file '{}' will be overwritten".format(outfile_path), file=sys.stderr)
    elif output_exists and not force:
        print("The output file '{}' already exists. Add the corresponding flag to force overwrite.".format(outfile_path), file=sys.stderr)
        return

    file = []
    with open (infile_path) as infile:
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


    with open(outfile_path, 'w') as outfile:
        outfile.write('\n'.join(newfile))

if __name__=="__main__":
    main()