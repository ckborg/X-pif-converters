import csv
import argparse
from pypif import pif
from pypif.obj import *


def netzsch_3500_to_pif(closed_csv):

    # create chemical system and property array
    my_pif = ChemicalSystem()
    my_pif.properties = []

    # Store index so that iteration can start at next row. Default to False when no header is found.
    header_row_index = False

    # Initialize arrays for heat capacity and conditions (time and temp)
    temp_array = []
    time_array = []
    heat_capacity_array = []

    # open csv, iterate through rows.
    with open(closed_csv, 'rU') as open_csv:
        reader = csv.reader(open_csv)
        for index, row in enumerate(reader):

            # meta data is stored above property with header column = row[0]

            # set values based on row[0]
            if '#IDENTITY:' in row[0]:
                my_pif.chemical_formula = row[1].strip()

            if "#INSTRUMENT:" in row[0]:
                measurement_device = Instrument(name=row[1].split(" ")[0], model=row[1].split(" ")[2])

            if "#SAMPLE MASS /mg:" in row[0]:
                prop = Property(name='sample mass', scalars=row[1], units='mg')
                my_pif.properties.append(prop)

            if "#DATE/TIME:" in row[0]:
                date = Value(name="Experiment date", scalars=row[1].strip())

            if "#TYPE OF CRUCIBLE:" in row[0]:
                crucible = Value(name="Crucible", scalars=row[1].strip()+" "+row[2].strip())

            if "#PROTECTIVE GAS:" in row[0]:
                atmosphere = Value(name="Atmosphere", scalars=row[1].strip())

            # Temp indicates header row. Define header_row_index.
            if '##Temp.' in row[0]:
                header_row_index = index

            # Iterate through values after header_row.
            if header_row_index:
                if index > header_row_index:
                    temp_array.append(row[0])
                    time_array.append(row[1])
                    heat_capacity_array.append(row[2])

    # define property and append scalar values
    heat_capacity = Property('C$_p$', scalars=heat_capacity_array, units='J/(gK)')
    temp = Value(name='Temperature', scalars=temp_array, units='$^\circ$C')
    time = Value(name='Time', scalars=time_array, units='min')

    # append conditions.
    heat_capacity.conditions = [temp, time, date, crucible, atmosphere]
    heat_capacity.instrument = measurement_device

    # append property to pif
    my_pif.properties.append(heat_capacity)

    # print dump to check format
    print (pif.dumps(my_pif, indent=4))

    return my_pif


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', nargs='*', help='path to DSC csv')

    args = parser.parse_args()

    for f in args.csv:
        print ("PARSING: ", f)
        pifs = netzsch_3500_to_pif(f)

        f_out = f.replace(".csv", ".json")
        pif.dump(pifs, open(f_out, "w"), indent=4)