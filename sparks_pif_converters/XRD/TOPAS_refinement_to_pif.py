import csv
import argparse
from pypif import pif
from pypif.obj import *
import os


def parse_TOPAS_refinement(TOPAS_refinement_file):
    '''
    Function that converts the output file from a TOPAS XRD refinement to a PIF.

    Args:
        TOPAS_refinement_file (csv or csv-formatted txt): The output file from a refinement.

    Returns:
        pif (object): A pif object containing exp, calc, and diff curves as properties.
    '''

    # Initialize arrays to hold values
    theta = []
    exp = []
    calc = []
    diff = []
    phase1 = []
    phase2 = []

    # read csv, iterate through rows
    reader = csv.reader(open(TOPAS_refinement_file, 'rb'))
    for index,  row in enumerate(reader):

        # append values
        if index > 1:
            theta.append(row[0])
            exp.append(row[1])
            calc.append(row[4])
            diff.append(row[5])
            phase1.append(row[6])
            phase2.append(row[7])

    # create system
    my_pif = ChemicalSystem()
    my_pif.names = [os.path.basename(f).rpartition(".")[0]]
    my_pif.properties = []

    # create properties
    p_exp = Property(name="Counts", scalars=exp, units="arbitrary units")
    p_exp.conditions = [Value(name="2$\\theta$", scalars=theta, units="$^\circ$"), Value(name="Data Type", scalars="")]
    p_exp.references = [Reference(figure=DisplayItem(number="1"))]

    p_calc = Property(name="Counts", scalars=calc, units="arbitrary units", data_type="FIT")
    p_calc.conditions = [Value(name="2$\\theta$", scalars=theta, units="$^\circ$"), Value(name="Data Type", scalars="")]
    p_calc.references = [Reference(figure=DisplayItem(number="1"))]

    p_diff = Property(name="Counts", scalars=diff, units="arbitrary units")
    p_diff.conditions = [Value(name="2$\\theta$", scalars=theta, units="$^\circ$"), Value(name="Data Type", scalars="")]
    p_diff.references = [Reference(figure=DisplayItem(number="1"))]

    p_1 = Property(name="Counts", scalars=phase1, units="arbitrary units", data_type="FIT")
    p_1.conditions = [Value(name="2$\\theta$", scalars=theta, units="$^\circ$"), Value(name="Data Type", scalars="")]
    p_1.references = [Reference(figure=DisplayItem(number="1"))]

    p_2 = Property(name="Counts", scalars=phase2, units="arbitrary units", data_type="FIT")
    p_2.conditions = [Value(name="2$\\theta$", scalars=theta, units="$^\circ$"), Value(name="Data Type", scalars="")]
    p_2.references = [Reference(figure=DisplayItem(number="1"))]

    # append properties
    my_pif.properties.extend([p_exp, p_calc, p_diff, p_1, p_2])

    return my_pif


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', nargs='*', help='path to 11-BM outfile')

    args = parser.parse_args()

    for f in args.csv:
        print("PARSING: {}".format(f))
        pifs = parse_TOPAS_refinement(f)
        f_out = f.replace(".txt", ".json")
        print("OUTPUT FILE: {}").format(f_out)
        pif.dump(pifs, open(f_out, "w"), indent=4)