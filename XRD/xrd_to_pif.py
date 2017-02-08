import csv
import argparse
from pypif import pif
from pypif.obj import *


def raw4_to_pif(closed_txt):

    # create chemical system and property array
    my_pif = ChemicalSystem()
    my_pif.properties = []

    # Store header index so that iteration can start at next row. Default to False when no header is found.
    header_line_index = False

    # initialize arrays for 2theta and intensity
    theta = []
    intensity = []

    # open text file, read lines, iterate through each line.
    with open(closed_txt, 'rU') as open_txt:
        lines = open_txt.readlines()
        for index, line in enumerate(lines):

            # clean up newline chars
            line = line.replace("\n", "")

            # search for keywords in line and set props accordingly
            if "Date=" in line:
                date = Value(name="Experiment date", scalars=line.split("=")[-1])
            if "ActuallyUsedLambda=" in line:
                wavelength = Value(name="X-ray wavelength", scalars=line.split("=")[-1])

            # data indicates header line
            if "[Data]" in line:
                header_line_index = index

            if header_line_index:
                if index > header_line_index:
                    theta.append(line.split(",")[0].strip())
                    intensity.append(line.split(",")[1].strip())

        # define prop and set scalars
        xrd = Property(name="Intensity", scalars=intensity, units="arb. unit")
        theta = Value(name="2$\\theta$", scalars=theta, units="$\circ$")
        xrd.conditions = [theta, date, wavelength]

        my_pif.properties.append(xrd)

        print (pif.dumps(my_pif, indent=4))

        return [my_pif]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', nargs='*', help='path to XRD txt file')

    args = parser.parse_args()

    for f in args.csv:
        print ("PARSING: ", f)
        pifs = raw4_to_pif(f)

        # add chemical_formula from filename.
        for system in pifs:
            system.chemical_formula = f.split("/")[-1].split("-")[0]

        f_out = f.replace(".txt", ".json")
        pif.dump(pifs, open(f_out, "w"), indent=4)