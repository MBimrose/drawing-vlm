from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
inlet_width = 30.0
inlet_height = 20.0
inlet_depth = wall_thickness + 2.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_spacing = 40.0
rib_thickness = 2.0
rib_height = 10.0
rib_count = 6

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

inlet_box = Pos(outer_radius - wall_thickness/2, 0, 0) * Box(inlet_depth, inlet_width, inlet_height)
solid_body = solid_body - inlet_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for x, y in [(-mount_hole_spacing/2, 0), (mount_hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, height/2) * Cylinder(mount_hole_dia/2, height + 10)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_inlet"
export_step(part, "output.step")