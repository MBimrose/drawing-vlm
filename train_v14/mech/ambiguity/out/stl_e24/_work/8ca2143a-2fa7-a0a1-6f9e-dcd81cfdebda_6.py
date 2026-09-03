from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
rib_width = 12.0
rib_thickness = 2.0
rib_height = 4.0
blind_hole_diameter = 5.0
blind_hole_depth = 10.0
blind_hole_offset_x = 30.0
blind_hole_offset_z = 4.0
screw_hole_diameter = 4.0
screw_hole_countersink_diameter = 7.0
screw_hole_countersink_angle = 90.0
screw_hole_offset_y = 15.0
screw_hole_offset_z = 4.0
chamfer_distance = 0.8

base = Box(jaw_length, jaw_width, jaw_thickness)
rib = Pos(0, 0, jaw_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
result = base + rib

blind_hole = Pos(blind_hole_offset_x - jaw_length/2, -jaw_width/2 + blind_hole_depth/2, blind_hole_offset_z - jaw_thickness/2) * Rot(90, 0, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result - blind_hole

screw_hole = Pos(jaw_length/2, screw_hole_offset_y, screw_hole_offset_z - jaw_thickness/2) * Rot(0, -90, 0) * CounterSinkHole(screw_hole_diameter/2, screw_hole_countersink_diameter/2, jaw_thickness, screw_hole_countersink_angle)
result = result - screw_hole

top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "jaw_with_rib_and_holes"
export_step(part, "output.step")