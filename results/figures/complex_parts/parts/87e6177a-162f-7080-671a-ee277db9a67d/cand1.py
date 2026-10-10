from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
slot_width = 12.0
slot_height = 8.0
chamfer_size = 1.0
hole_diameter = 4.0
hole_offset_radius = 30.0
rib_count = 6
rib_thickness = 2.0
rib_height = 3.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot = Pos(outer_radius - wall_thickness/2, 0, 0) * Box(slot_width, slot_height, wall_thickness + 0.2)
solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for x, y in [(hole_offset_radius, 0), (-hole_offset_radius, 0)]:
    solid_body = solid_body - Pos(x, y, height/2) * Cylinder(hole_diameter/2, height + 10)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_height, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")