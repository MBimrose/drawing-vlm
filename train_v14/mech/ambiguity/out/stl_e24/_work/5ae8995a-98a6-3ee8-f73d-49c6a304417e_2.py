from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 20.0
length = 70.0
slot_width = 4.0
slot_length = 50.0
slot_depth = 3.0
set_screw_diameter = 5.0
set_screw_offset = 20.0
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius
slot_center_z = length / 2.0
slot_center_x = outer_radius - slot_depth / 2.0
set_screw_z = slot_center_z + slot_length / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(0, slot_center_x, 0) * Box(slot_width, slot_depth, slot_length)
solid_body = solid_body - slot_box

set_screw = Pos(0, outer_radius - wall_thickness / 2.0, set_screw_z) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness + 0.5)
solid_body = solid_body - set_screw

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "hollow_cylinder_with_slot_and_setscrew"
export_step(part, "output.step")