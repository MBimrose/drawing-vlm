from build123d import *
import math

outer_diameter = 30.0
outer_radius = outer_diameter / 2.0
length = 80.0
wall_thickness = 4.0
groove_pitch = 20.0
groove_depth = 3.0
groove_width = 2.0
groove_margin = 1.0
set_screw_diameter = 2.5
set_screw_offset = 20.0
chamfer_size = 0.5
tab_width = 12.0
tab_height = 10.0
tab_thickness = 3.0
tab_overlap = 1.0

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(top_face.edges() + bottom_face.edges(), chamfer_size)

tab_center_x = outer_radius - tab_thickness / 2.0 + tab_overlap
tab = Pos(tab_center_x, 0, length / 2.0) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

groove_length = length - 2 * groove_margin
num_pts = 200
helix_pts = []
for i in range(num_pts):
    t = i / (num_pts - 1)
    z = groove_margin + t * groove_length
    angle = 2 * math.pi * (z / groove_pitch)
    r = outer_radius - groove_depth / 2.0
    helix_pts.append(Vector(r * math.cos(angle), r * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_wire = bl.wire()

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch

groove_solid = sweep(sections=groove_face, path=helix_wire)
solid_body = solid_body - groove_solid

set_screw = Pos(outer_radius - wall_thickness / 2.0, 0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness)
solid_body = solid_body - set_screw

part = solid_body
part.name = "grooved_cylinder_with_tab"
export_step(part, "output.step")