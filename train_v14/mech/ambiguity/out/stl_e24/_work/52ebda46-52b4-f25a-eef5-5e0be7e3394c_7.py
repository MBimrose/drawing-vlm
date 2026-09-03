from build123d import *

bore_diameter = 20.0
collar_thickness = 10.0
collar_width = 30.0
groove_width = 5.0
groove_depth = 2.0
set_screw_hole_diameter = 4.0
set_screw_counterbore_diameter = 8.0
set_screw_counterbore_depth = 4.0
chamfer_size = 0.8
outer_radius = bore_diameter/2 + collar_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((bore_diameter/2, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, collar_width))
            l3 = Line(l2@1, (bore_diameter/2 + groove_width, collar_width))
            l4 = Line(l3@1, (bore_diameter/2 + groove_width, collar_width - groove_depth))
            l5 = Line(l4@1, (bore_diameter/2, collar_width - groove_depth))
            l6 = Line(l5@1, (bore_diameter/2, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
import math
for i in range(4):
    angle_deg = i * 90
    angle_rad = math.radians(angle_deg)
    r = outer_radius - collar_thickness/2
    x = r * math.cos(angle_rad)
    y = r * math.sin(angle_rad)
    z = collar_width/2 - set_screw_counterbore_depth/2
    cbore = Pos(x, y, z) * Rot(0, 90, angle_deg) * Cylinder(set_screw_counterbore_diameter/2, set_screw_counterbore_depth)
    solid_body = solid_body - cbore
    r2 = outer_radius - collar_thickness/2
    x2 = r2 * math.cos(angle_rad)
    y2 = r2 * math.sin(angle_rad)
    z2 = collar_width/2
    hole = Pos(x2, y2, z2) * Rot(0, 90, angle_deg) * Cylinder(set_screw_hole_diameter/2, collar_thickness + 2)
    solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "collar_with_groove_and_set_screw_holes"
export_step(part, "output.step")