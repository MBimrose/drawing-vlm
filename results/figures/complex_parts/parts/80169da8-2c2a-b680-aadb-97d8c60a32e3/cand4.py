from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
length = 40.0
rib_width = 6.0
rib_height = 12.0
rib_depth = 3.0
rib_count = 4
chamfer_size = 0.5
tab_width = 10.0
tab_height = 6.0
tab_thickness = 2.0
tab_hole_dia = 3.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

tab = Pos(0, outer_radius + tab_thickness/2, 0) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

hole = Pos(0, outer_radius + tab_thickness/2, 0) * Rot(90, 0, 0) * Cylinder(tab_hole_dia/2, tab_thickness + 1)
solid_body = solid_body - hole

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_depth/2, 0, 0) * Box(rib_depth, rib_width, rib_height)
    solid_body = solid_body - rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_tabs_and_ribs"
export_step(part, "output.step")