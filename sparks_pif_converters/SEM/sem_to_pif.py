import csv
import argparse
from pypif import pif
from pypif.obj import *
from PIL import Image


def s3000_metadata_to_pif(closed_txt):

    # create chemical system and property array
    my_pif = ChemicalSystem()
    my_pif.properties = []
    my_pif.names = [closed_txt.split("/")[-1].split(".")[0]]

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


def convert_tif_to_jpeg(tiff_image):

    im = Image.open(tiff_image)
    jpeg_path = tiff_image.replace(".tif", ".jpeg")
    im.save(jpeg_path, "JPEG")
    print("CONVERTED: %s to %s" % (tiff_image, tiff_image.replace(".tif", ".jpeg")))

    return jpeg_path

def image_to_pif(image_path):

    print("PARSING: {}").format(image_path)

    file_type = image_path.split(".")[-1]

    if file_type == "tif":
        jpeg_path = convert_tif_to_jpeg(image_path)
        image_to_pif(jpeg_path)
        return

    my_pif = ChemicalSystem()
    my_pif.ids = [image_path.split("/")[-1].split("_")[0]]
    my_pif.names = [image_path.split("/")[-1].split(".")[0]]
    my_pif.properties = [Property(name="SEM", files=FileReference(mime_type="image/"+file_type, relative_path=image_path))]

    return [my_pif]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('images', nargs='*', help='path to SEM images (.tif, .jpeg, .bmp)')

    args = parser.parse_args()

    for f in args.images:
        system = image_to_pif(f)
        f_out = f.split(".")[0] + ".json"
        print(f_out)
        pif.dump(system, open(f_out, "w"), indent=4)