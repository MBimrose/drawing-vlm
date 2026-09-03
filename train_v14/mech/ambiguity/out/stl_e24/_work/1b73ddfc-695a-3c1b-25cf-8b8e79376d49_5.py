from build123d import *

plate_length = 60.0
plate_width = 40.0
plate_thickness = 8.0
hole_diameter = 4.0
countersink_diameter = 5.0
countersink_angle = 82.0

with BuildPart() as p:
    Box(plate_length, plate_width, plate_thickness)
    CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness/2, countersink_angle)

part = p.part
part.name = "plate_with_countersink"
export_step(part, "output.step")