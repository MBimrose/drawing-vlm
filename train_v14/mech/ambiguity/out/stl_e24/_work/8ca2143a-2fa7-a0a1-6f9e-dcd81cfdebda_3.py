from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
notch_width = 10.0
notch_depth = 4.0
hole_diameter = 5.0
hole_depth = 10.0
hole_offset_x = 30.0
chamfer_distance = 1.0
rib_height = 4.0
rib_width = 12.0
rib_thickness = 2.0

base = Box(jaw_length, jaw_width, jaw_thickness)

notch = Pos(jaw_length/2 - notch_depth/2, jaw_width/2, 0) * Box(notch_depth, notch_width, notch_depth)
base = base - notch

hole = Pos(hole_offset_x - jaw_length/2, -jaw_width/2 + hole_depth/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, hole_depth)
base = base - hole

rib = Pos(0, 0, jaw_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
base = base + rib

top_edges = base.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-2:]
base = chamfer(top_edges, chamfer_distance)

part = base
part.name = "jaw_with_notch_hole_rib"
export_step(part, "output.step")