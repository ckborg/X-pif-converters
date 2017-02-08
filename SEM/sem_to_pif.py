import csv
import argparse
from pypif import pif
from pypif.obj import *

def s3000_metadata_to_pif(closed_txt):

    # create chemical system and property array
    my_pif = ChemicalSystem()
    my_pif.properties = []

    with open(closed_txt, 'rU') as open_txt:
        lines = open_txt.readlines()
        for index, line in enumerate(lines):

            # clean up newline chars
            line = line.replace("\n", "")

            # search for keywords in line and set props accordingly
            if "Date=" in line:
                date = Value(name="Experiment date", scalars=line.split("=")[-1])
            if "Magnification" in line:
                mag = Value(name="Magnification", scalars=line.split("=")[-1])
            if "AcceleratingVoltage" in line:
                volt = Value(name="Accelerating voltage", scalars=line.split("=")[-1].split("Volt")[0], units="Volt")
            if "EmissionCurrent" in line:
                current = Value(name="Emission current", scalars=line.split("=")[-1].split("nA")[0], units="nA")
            if "WorkingDistance" in line:
                wd = Value(name="Working distance", scalars=line.split("=")[-1].split("um")[0], units="$\mu$m")
            if "Vacuum" in line:
                vac = Value(name="Vacuum", scalars=line.split("=")[-1])

    SEM = Property(name="SEM")
    SEM.conditions = [date, mag, volt, current, wd, vac]
    my_pif.properties.append(SEM)

    return my_pif


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('txt', nargs='*', help='path to SEM files')

    args = parser.parse_args()

    # empty array for pifs
    pifs = []

    # first iterate through dir and look for metadata file. Parse metadata if exists.
    for f in args.txt:
        if ".txt" in f:
            print ("PARSING: ", f)
            metadata_pif = s3000_metadata_to_pif(f)
            metadata_pif.names = [f.split("/")[-1].split(".")[0]]
            pifs.append(metadata_pif)

    # second iterate through dir and look for .bmp image.
    for f in args.txt:
        if ".bmp" in f:
            print ("PARSING: ", f)

            for system in pifs:

                # check for same name
                if system.names == [f.split("/")[-1].split(".")[0]]:

                    # append file ref to pif from metadata output.
                    if system.properties:
                        for prop in system.properties:
                            if prop.name == "SEM":
                                prop.files = FileReference(mime_type="image/bmp", relative_path=f)

            print (pif.dumps(pifs, indent=4))

            # output file
            f_out = f.replace(".bmp", ".json")
            pif.dump(pifs, open(f_out, "w"), indent=4)