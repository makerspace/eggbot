import sys
import os
import argparse

COMMAND_PEN_DOWN_TEMPLATE = "M3 S31 (Pen down)\nG4 P{wait_time:.2f} (wait)"
COMMAND_PEN_UP_TEMPLATE = "M3 S90 (Pen up)\nG4 P{wait_time:.2f} (wait)"
GCODE_EXTENSIONS = (".gcode", ".ngc")

class ConversionStats(object):
    def __init__(self):
        self.g_command_count = 0
        self.path_count = 0
    
    def increment_g_command_count(self):
        self.g_command_count = self.g_command_count + 1

    def increment_path_count(self):
        self.path_count = self.path_count + 1

    def __str__(self):
        return "Number of paths: {}\nNumber of G-commands: {}".format(self.path_count, self.g_command_count)

def preprocess_lines(lines, wait_time):
    lines_without_m = []
    for line in lines:
        if line[0].upper() not in 'M%': #remove initial M-commands
            lines_without_m.append(line.rstrip())

    stats = ConversionStats()
    COMMAND_PEN_DOWN = COMMAND_PEN_DOWN_TEMPLATE.format(wait_time=wait_time)
    COMMAND_PEN_UP = COMMAND_PEN_UP_TEMPLATE.format(wait_time=wait_time)

    processed_lines = []
    processed_lines.append('%\n')
    pen_is_down = False;
    for line in lines_without_m:
        line_words = line.upper().split()
        new_line_words = []
        if len(line_words)>0 and line_words[0][0] == 'G' and int(line_words[0][1:]) <= 9: # its a gcode motion line
            stats.increment_g_command_count()
            for word in line_words:
                is_pen_command = (word[0] == 'Z')
                if is_pen_command:
                    pen_should_be_down = (float(word[1:]) <= 0.0)
                    if pen_should_be_down and not pen_is_down:
                        stats.increment_path_count()
                        processed_lines.append(COMMAND_PEN_DOWN)
                    elif not pen_should_be_down and pen_is_down:
                        processed_lines.append(COMMAND_PEN_UP)
                    pen_is_down = pen_should_be_down
                else:
                    new_line_words.append(word)
            if len(new_line_words) > 2 or (len(new_line_words) > 1 and new_line_words[1][0] != 'F'): # get rid of empty feed command
                processed_lines.append(" ".join(new_line_words))
        else:
            processed_lines.append(line)

    processed_lines.append('(M5 fake stop spindle)')
    processed_lines.append('%\n')

    return processed_lines, stats

def preprocess_file(infile_path, outfile_path, wait_time):
    infile_lines = []
    with open(infile_path, 'r') as infile:
        for fileline in infile:
            infile_lines.append(fileline)

    outfile_lines, stats = preprocess_lines(infile_lines, wait_time)

    with open(outfile_path, 'w') as outfile:
        outfile.write('\n'.join(outfile_lines))

    return stats

def main():
    parser = argparse.ArgumentParser(description="Converts gcode files from inkscape so they can be used by an eggbot (e.g. replaces z-movements with pen movements)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("filename", help="The .gcode file to convert to eggbot compatible gcode")
    parser.add_argument("--force", "-f", action="store_true", help="Force usage of input file even if wrong extension, and output file even if it will be overwritten.")
    parser.add_argument("--wait-time", "-w", default=0.25, type=float, help="Time to wait between pen up/down commands.")
    parser.add_argument("--output", "-o", default=argparse.SUPPRESS, help="Output file name to use. Derived from input file if omitted.")
    parser.add_argument("--no-stat", action="store_true", help="Do not print stats collected during conversion.")
    ns = parser.parse_args()

    # Get passed arguments
    infile_path = ns.filename
    force = ns.force
    wait_time = ns.wait_time
    print_stats = not ns.no_stat

    # Check input file
    infile_basename, infile_extension = os.path.splitext(infile_path)
    if infile_extension not in GCODE_EXTENSIONS and not force:
        print("Wrong input file extension. Exiting", file=sys.stderr)
        return

    # Get output file path
    if "output" in ns:
        outfile_path = ns.output
    else:
        outfile_path = infile_basename + ".eggbot" + infile_extension
    print("Output file: '{}'".format(outfile_path), file=sys.stderr)

    # Check output file
    output_exists = os.path.isfile(outfile_path)
    if output_exists and force:
        print("The output file already exists and will be overwritten.", file=sys.stderr)
    elif output_exists and not force:
        print("The output file already exists. Exiting", file=sys.stderr)
        return

    stats = preprocess_file(infile_path, outfile_path, wait_time)
    if print_stats:
        print(stats)

if __name__=="__main__":
    main()