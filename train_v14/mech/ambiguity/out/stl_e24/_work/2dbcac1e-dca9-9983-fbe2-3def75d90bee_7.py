from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 15.0
rib_height = 3.0
hole_diameter = 6.5
hole_offset_x = 30.0
hole_offset_y = 20.0
chamfer_distance = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
solid = base + rib

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 10
for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = solid
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")