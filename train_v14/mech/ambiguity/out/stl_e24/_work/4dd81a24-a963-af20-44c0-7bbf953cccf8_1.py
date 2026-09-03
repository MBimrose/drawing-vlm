from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
rib_height = 2.0
rib_thickness = 2.0
rib_offset = 3.0
hole_diameter = 4.5
hole_spacing_x = 30.0
hole_spacing_y = 30.0
hole_offset_x = 10.0
hole_offset_y = 10.0
chamfer_size = 2.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, -plate_width/2 + rib_offset, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_offset, rib_thickness, rib_height)
result = base + rib

hole_positions = [
    (-plate_length/2 + hole_offset_x, -plate_width/2 + hole_offset_y),
    (-plate_length/2 + hole_offset_x + hole_spacing_x, -plate_width/2 + hole_offset_y),
    (-plate_length/2 + hole_offset_x, -plate_width/2 + hole_offset_y + hole_spacing_y),
    (-plate_length/2 + hole_offset_x + hole_spacing_x, -plate_width/2 + hole_offset_y + hole_spacing_y),
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 2)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")