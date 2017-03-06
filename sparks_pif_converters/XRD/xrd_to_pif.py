import csv
import argparse
from pypif import pif
from pypif.obj import *
from pyxrd.file_parsers.xrd_parsers import BrkRAWParser
import re


def raw4_txt_to_pif(closed_txt):

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

            if header_line_index and index > header_line_index + 1:
                theta.append(float(line.split(",")[0].strip()))
                intensity.append(int(line.split(",")[1].strip()))

    # define prop and set scalars
    xrd = Property(name="Intensity", scalars=intensity, units="arb. unit")
    I_max_index = intensity.index(max(intensity))
    I_max = Property(name="2$\\theta$ (I$_{max}$)", scalars=theta[I_max_index], units="$^\circ$")
    theta = Value(name="2$\\theta$", scalars=theta, units="$^\circ$")
    xrd.conditions = [theta, date, wavelength]

    my_pif.properties.append(xrd)
    my_pif.properties.append(I_max)

    return [my_pif]


def raw_to_pif(raw_xrd_file):

    # parses .raw file
    try:
        parsed_raw = BrkRAWParser.parse(raw_xrd_file)

        my_pif = ChemicalSystem()
        my_pif.chemical_formula = raw_xrd_file.split("/")[-1].replace(".raw", "").split("_")[0]
        my_pif.ids = "".join(raw_xrd_file.split("/")[-1].replace(".raw", "").split("_")[1:])

        my_pif.properties = []

        theta = []
        intensity = []
        for xrd in parsed_raw:
            # xrd.date
            a1 = Value(name="wavelength of $\\alpha_1$", scalars=xrd.alpha1, units="$\AA$")
            a2 = Value(name="wavelength of $\\alpha_2$", scalars=xrd.alpha2, units="$\AA$")

            for ndarray in xrd.data:
                theta.append(float(ndarray[0]))
                intensity.append(float(ndarray[1]))

        peaks = Property(name="Intensity", scalars=intensity, units="arb. unit")
        I_max_index = intensity.index(max(intensity))
        I_max = Property(name="2$\\theta$ (I$_{max}$)", scalars=theta[I_max_index], units="$^\circ$")
        twotheta = Value(name="2$\\theta$", scalars=theta, units="$^\circ$")
        peaks.conditions = [twotheta, a1, a2]

        my_pif.properties.append(peaks)
        my_pif.properties.append(I_max)

        return my_pif

    except Exception as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', help='path to XRD files (.raw, .txt)')

    args = parser.parse_args()

    for f in args.files:

        if ".txt" in f:
            print ("PARSING: {}".format(f))
            pifs = raw4_txt_to_pif(f)
            f_out = f.replace(".txt", ".json")
            print ("OUTPUT: {}".format(f_out))
            pif.dump(pifs, open(f_out, "w"), indent=4)

        if ".raw" in f:
            print ("PARSING: {}".format(f))
            pifs = raw_to_pif(f)
            f_out = f.replace(".raw", ".json")
            print ("OUTPUT: {}".format(f_out))
            pif.dump(pifs, open(f_out, "w"), indent=4)
