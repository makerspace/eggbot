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

    # Check input file
    infile_basename, infile_extension = os.path.splitext(infile_path)
    if infile_extension != ".gcode" and not force:
        print("Wrong input file extension. Exiting", file=sys.stderr)
        return

    # Check output file
    outfile_path = infile_basename + ".eggbot" + infile_extension
    output_exists = os.path.isfile(outfile_path)
    if output_exists and force:
        print("The output file '{}' already exists and will be overwritten.".format(outfile_path), file=sys.stderr)
    elif output_exists and not force:
        print("The output file '{}' already exists. Exiting".format(outfile_path), file=sys.stderr)
        return

    infile_lines = []
    with open(infile_path, 'r') as infile:
        for fileline in infile:
            if fileline[0].upper() not in 'M%': #remove initial M-commands
                infile_lines.append(fileline.rstrip())

    outfile_lines = []
    outfile_lines.append('%\n')
    pen_is_down = False;
    for fileline in infile_lines:
        words = fileline.upper().split()
        newwords = []
        if len(words)>0 and words[0][0] == 'G' and int(words[0][1:]) <= 9: # its a gcode motion line
            for word in words:
                is_pen_command = (word[0] == 'Z')
                if is_pen_command:
                    pen_should_be_down = (float(word[1:]) <= 0.0)
                    if pen_should_be_down and not pen_is_down:
                        outfile_lines.append(COMMAND_PEN_DOWN)
                    elif not pen_should_be_down and pen_is_down:
                        outfile_lines.append(COMMAND_PEN_UP)
                    pen_is_down = pen_should_be_down
                else :
                    newwords.append(word)
            if len(newwords) > 2 or (len(newwords) > 1 and newwords[1][0] != 'F'): # get rid of empty feed command
                outfile_lines.append(" ".join(newwords))
        else:
            outfile_lines.append(fileline)

    outfile_lines.append('(M5 fake stop spindle)')
    outfile_lines.append('%\n')


    with open(outfile_path, 'w') as outfile:
        outfile.write('\n'.join(outfile_lines))

if __name__=="__main__":
    main()