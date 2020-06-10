import subprocess
import shapefile
import pathlib

from json import dumps
from shapely.geometry import (mapping, shape)
from argparse import ArgumentParser
from sys import stdout, stderr


class ShapeRecordHelper():
    def __init__(self, fields):
        self.fields = fields
        self.field_name = [field[0] for field in fields]

    def to_geojson(self, shapeRecord: shapefile.ShapeRecord):
        atr = dict(zip(self.field_name, shapeRecord.record))
        image_no = atr['image_no']

        if not image_no:
            raise TypeError("missing 1 required field: 'image_no'")

        if shapeRecord.shape.shapeTypeName == 'NULL':
            raise ValueError('Shape type "NULL" cannot be '
                             'represented as GeoJSON.\n')

        geom = shapeRecord.shape.__geo_interface__

        sh = shape(geom)
        if not sh.is_valid:  # fix self intersect
            geom = mapping(sh.buffer(0))

        return dict(type="Feature", geometry=geom, properties=atr)


class GDALCommand():
    def __init__(self, input_geojson, input_raster, output_clip):
        self.input_geojson = input_geojson
        self.input_raster = input_raster
        self.output_clip = output_clip

    def __str__(self):
        return ' '.join(self.get_args())

    def get_args(self):
        return ["gdalwarp", "-cutline", str(self.input_geojson),
                "-crop_to_cutline", "-dstalpha", str(self.input_raster),
                str(self.output_clip)]


def getSettings():
    ap = ArgumentParser()
    ap.add_argument('-i', '--input_folder', required=True,
                    help='The folder that contains the raster files.')
    ap.add_argument('-o', '--output_path', required=True,
                    help='The path where the geojson files will be created')
    ap.add_argument('-n', '--no_run', action='store_true',
                    help='Do not execute command but write geoJSON file.')
    ap.add_argument('-s', '--simulate', action='store_true',
                    help='Do not execute command and dont write anything on disk.')
    ap.add_argument('shape_file',
                    help='A shape file with the field "image_no" in it.')

    return ap.parse_args()


def main():
    config = getSettings()
    output_path = pathlib.Path(config.output_path).resolve()
    input_folder = pathlib.Path(config.input_folder).resolve()

    if not output_path.exists():
        output_path.mkdir()

    with shapefile.Reader(config.shape_file) as reader:
        shapeRecordHelper = ShapeRecordHelper(reader.fields[1:])
        i = 0

        commands = []

        def print_log(std, msg):
            std.write(f"Record n°{i} ({config.shape_file}) - {msg}\n")

        for sr in reader.shapeRecords():
            i += 1
            try:
                geom = shapeRecordHelper.to_geojson(sr)
            except Exception as e:
                print_log(stderr, e)
                continue

            # Get Files names
            image_no = geom["properties"]['image_no']
            raster = input_folder / pathlib.Path(image_no)
            filegeojson = output_path / raster.with_suffix('.geojson').name

            # Generate commande line
            outputFile = output_path / (
                raster.with_suffix('').name + "_clip" + raster.suffix)

            commands.append(
                GDALCommand(filegeojson, raster.resolve(), outputFile))

            if not config.simulate:
                filegeojson.write_text(dumps(geom, indent=2), 'UTF-8')

    for command in commands:
        print(command)

    if not (config.no_run or config.simulate):
        i = 0
        length = len(commands)
        for command in commands:
            i += 1
            stderr.write(f'Command {i}/{length}: {command}\n')
            try:
                result = subprocess.run(command.get_args())
            except Exception as e:
                stderr.write(f"ERROR: {e}\n")


if __name__ == '__main__':
    main()
