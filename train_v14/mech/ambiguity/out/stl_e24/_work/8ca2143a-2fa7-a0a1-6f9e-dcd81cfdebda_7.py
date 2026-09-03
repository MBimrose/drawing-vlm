from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
rib_height = 4.0
rib_width = 12.0
rib_thickness = 2.0
hole_diameter = 5.0
hole_offset_x = 30.0
hole_offset_z = 4.0
countersink_diameter = 6.0
countersink_depth = 4.0
countersink_angle = 82.0
chamfer_size = 0.5

base = Box(jaw_length, jaw_width, jaw_thickness)
rib = Pos(0, 0, jaw_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = base + rib

hole_x = hole_offset_x - jaw_length/2
hole_z = hole_offset_z - jaw_thickness/2
hole = Pos(hole_x, -jaw_width/2 + jaw_thickness/2, hole_z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, jaw_thickness)
solid_body = solid_body - hole

csk = Pos(jaw_length/2, jaw_width/2 - countersink_depth/2, 0) * Rot(90, 0, 0) * CounterSinkHole(countersink_diameter/2, countersink_depth/2, countersink_depth, countersink_angle)
solid_body = solid_body - csk

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "jaw_with_rib"
export_step(part, "output.step")