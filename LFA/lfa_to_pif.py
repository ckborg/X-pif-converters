import csv
import argparse
from pypif import pif
from pypif.obj import *

def lfa457_to_pif(closed_csv):

    # create chemical system and property array
    my_pif = ChemicalSystem()
    my_pif.properties = []

    # Store index so that iteration can start at next row. Default to False when no header is found.
    header_row_index = False

    # Initialize arrays for diffusivity and conditions (time and temp)
    temp_array = []
    time_array = []
    diffusivity_array = []

    with open(closed_csv, 'rU') as open_csv:
        reader = csv.reader(open_csv)
        for index, row in enumerate(reader):

            # meta data is stored above property with header column = row[0]

            # ensure row has values
            if len(row) != 0:

                # set properties based on row[0]
                if '#Material' in row[0]:
                    my_pif.chemical_formula = row[1].strip()

                if "#Instrument" in row[0]:
                    measurement_device = Instrument(name=row[1].replace("#", ""))

                if "#Thickness_RT/mm" in row[0]:
                    thickness = Property(name="Thickness", scalars=row[1])

                if "#Diameter/mm" in row[0]:
                    diameter = Property(name="Diameter", scalars=row[1])

                if "#Date" in row[0]:
                    date = Value(name="Experiment date", scalars=row[1].strip())

                if "#Atmosphere" in row[0]:
                    atmosphere = Value(name="Atmosphere", scalars=row[1].strip())

                if "#Gas_flow/(ml/min)" in row[0]:
                    flow = Value(name="Flow rate", scalars=row[1], units="ml/min")

                # shot number defines header_row
                if "#Shot number" in row[0]:
                    header_row_index = index

                # we could find header row and collect all rows after it or regex row[0] for a decimal number
                if header_row_index:
                    if index > header_row_index:
                        temp_array.append(row[2])
                        time_array.append(row[1])
                        diffusivity_array.append(row[3]+"$\pm$"+row[4])

        heat_capacity = Property('Diffusivity', scalars=diffusivity_array, units='mm$^2$/s')
        temp = Value(name='Temperature', scalars=temp_array, units='$^\circ$C')
        time = Value(name='Time', scalars=time_array, units='min')

        heat_capacity.conditions = [temp, time, date, atmosphere, flow]
        heat_capacity.instrument = measurement_device

        my_pif.properties.append(heat_capacity)
        my_pif.properties.append(thickness)
        my_pif.properties.append(diameter)

        print (pif.dumps(my_pif, indent=4))

        return my_pif


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', nargs='*', help='path to LFA csv')

    args = parser.parse_args()

    for f in args.csv:
        print ("PARSING: ", f)
        pifs = lfa457_to_pif(f)

        f_out = f.replace(".csv", ".json")
        pif.dump(pifs, open(f_out, "w"), indent=4)