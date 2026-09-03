from build123d import *
import math

outer_diameter = 60.0
height = 30.0
wall_thickness = 5.0
pocket_depth = 20.0
central_hole_diameter = 10.0
slot_width = 4.0
slot_height = 10.0
slot_count = 12
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, height/2 - pocket_depth/2) * Cylinder(inner_radius, pocket_depth)
solid_body = solid_body - pocket

central_hole = Cylinder(central_hole_diameter/2, height)
solid_body = solid_body - central_hole

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2, 0, 0) * Box(wall_thickness, slot_width, slot_height)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_slots"
export_step(part, "output.step")