from build123d import *
import math

outer_diameter = 45.0
inner_diameter = 20.0
collar_length = 30.0
step_length = 5.0
step_diameter = 40.0
groove_width = 6.0
groove_depth = 2.0
hole_diameter = 4.0
hole_rows = 2
holes_per_row = 4
row_spacing = 10.0
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
step_radius = step_diameter / 2.0
groove_radius = step_radius - groove_depth

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, collar_length))
            l2 = Line(l1@1, (step_radius, collar_length))
            l3 = Line(l2@1, (step_radius, collar_length - step_length))
            l4 = Line(l3@1, (inner_radius, collar_length - step_length))
            l5 = Line(l4@1, (inner_radius, 0))
            l6 = Line(l5@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove_z = collar_length - step_length - groove_width / 2.0
groove = Pos(0, 0, groove_z) * Cylinder(groove_radius, groove_width)
solid_body = solid_body - groove

hole_r = hole_diameter / 2.0
hole_len = outer_radius - inner_radius
hole_center_z = collar_length / 2.0
for i in range(hole_rows):
    z_offset = (i - (hole_rows - 1) / 2.0) * row_spacing
    z_pos = hole_center_z + z_offset
    for j in range(holes_per_row):
        angle_deg = j * 360.0 / holes_per_row
        hole = Rot(0, 0, angle_deg) * Pos(outer_radius - hole_len / 2.0, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_r, hole_len)
        solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "collar_with_groove_and_holes"
export_step(part, "output.step")