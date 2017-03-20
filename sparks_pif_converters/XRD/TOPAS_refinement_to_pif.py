import csv
import argparse
from pypif import pif
from pypif.obj import *
import os
import pandas as pd


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
            theta.append(Scalar(value=row[0]))
            exp.append(Scalar(value=row[1]))
            calc.append(Scalar(value=row[4]))
            diff.append(Scalar(value=row[5]))
            phase1.append(Scalar(value=row[6]))
            phase2.append(Scalar(value=row[7]))

    downsampled_array = downsample_data_points(TOPAS_refinement_file)

    # create system
    my_pif = ChemicalSystem()
    my_pif.names = [os.path.basename(f).rpartition(".")[0]]
    my_pif.properties = []

    # create properties
    p_exp = Property(name="Counts", scalars=downsampled_array[1], units="arbitrary units")
    p_exp.conditions = [Value(name="2$\\theta$", scalars=downsampled_array[0], units="$^\circ$"), Value(name="label", scalars="data")]
    p_exp.references = [Reference(figure=DisplayItem(number="1"))]

    p_calc = Property(name="Counts", scalars=downsampled_array[2], units="arbitrary units", data_type="FIT")
    p_calc.conditions = [Value(name="2$\\theta$", scalars=downsampled_array[0], units="$^\circ$"), Value(name="label", scalars="model")]
    p_calc.references = [Reference(figure=DisplayItem(number="1"))]

    #p_diff = Property(name="Counts", scalars=diff, units="arbitrary units")
    #p_diff.conditions = [Value(name="2$\\theta$", scalars=theta, units="$^\circ$"), Value(name="Data Type", scalars="")]
    #p_diff.references = [Reference(figure=DisplayItem(number="1"))]

    p_1 = Property(name="Counts", scalars=downsampled_array[4], units="arbitrary units", data_type="FIT")
    p_1.conditions = [Value(name="2$\\theta$", scalars=downsampled_array[0], units="$^\circ$"), Value(name="label", scalars="p1")]
    p_1.references = [Reference(figure=DisplayItem(number="1"))]

    p_2 = Property(name="Counts", scalars=downsampled_array[5], units="arbitrary units", data_type="FIT")
    p_2.conditions = [Value(name="2$\\theta$", scalars=downsampled_array[0], units="$^\circ$"), Value(name="label", scalars="p2")]
    p_2.references = [Reference(figure=DisplayItem(number="1"))]

    # append properties
    my_pif.properties.extend([p_exp, p_calc, p_1, p_2])

    return my_pif


def downsample_data_points(TOPAS_refinement_file):

    df = pd.read_csv(TOPAS_refinement_file, skiprows=1)
    exp_diff = 0.2*(max(df["11bmb_667_100K.xye"]) - min(df["11bmb_667_100K.xye"]))
    calc_diff = 0.2*(max(df["Ycalc"]) - min(df["Ycalc"]))
    diff_diff = 0.2*(max(df["Diff"]) - min(df["Diff"]))
    p1_diff = 0.2*(max(df["CoZnMn"]) - min(df["CoZnMn"]))
    p2_diff = 0.2*(max(df["Structure"]) - min(df["Structure"]))

    d_theta = [Scalar(value=df["'x"][0])]
    d_exp = [Scalar(value=df["11bmb_667_100K.xye"][0])]
    d_calc = [Scalar(value=["Ycalc"][0])]
    d_diff = [Scalar(value=["Diff"][0])]
    d_p1 = [Scalar(value=["CoZnMn"][0])]
    d_p2 = [Scalar(value=["Structure"][0])]

    count = 0

    for index, (x, exp, calc, diff, p1, p2) in enumerate(zip(df["'x"][1:], df["11bmb_667_100K.xye"][1:], df["Ycalc"][1:], df["Diff"][1:], df["CoZnMn"][1:], df["Structure"][1:])):

        if count > 100:
            count = 0
            d_theta.append(Scalar(value=x))
            d_exp.append(Scalar(value=exp))
            d_calc.append(Scalar(value=calc))
            d_diff.append(Scalar(value=diff))
            d_p1.append(Scalar(value=p1))
            d_p2.append(Scalar(value=p2))

        if abs(exp-df["11bmb_667_100K.xye"][index]) < exp_diff and abs(calc-df["Ycalc"][index]) < calc_diff and\
            abs(calc - df["Diff"][index]) < diff_diff and abs(calc-df["CoZnMn"][index]) < p1_diff and\
                abs(calc - df["Structure"][index]) < p2_diff:
            count += 1

        else:
            d_theta.append(Scalar(value=x))
            d_exp.append(Scalar(value=exp))
            d_calc.append(Scalar(value=calc))
            d_diff.append(Scalar(value=diff))
            d_p1.append(Scalar(value=p1))
            d_p2.append(Scalar(value=p2))

    return [d_theta, d_exp, d_calc, d_diff, d_p1, d_p2]


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