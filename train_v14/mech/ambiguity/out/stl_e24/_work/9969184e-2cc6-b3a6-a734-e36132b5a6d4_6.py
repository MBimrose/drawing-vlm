from build123d import *
import math

outer_diameter = 40.0
inner_diameter = 20.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
groove_width = 3.0
groove_depth = 2.0
groove_pitch = 12.0
counterbore_diameter = 10.0
counterbore_depth = 8.0
through_hole_diameter = 6.0
counterbore_offset = outer_diameter / 2.0 - wall_thickness / 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
groove_radius = outer_radius - groove_depth

solid_body = Pos(0, 0, length / 2) * (Cylinder(outer_radius, length) - Cylinder(inner_radius, length))

num_pts = 200
helix_pts = []
for i in range(num_pts):
    t = i / (num_pts - 1)
    z = t * length
    angle = 2 * math.pi * z / groove_pitch
    helix_pts.append(Vector(groove_radius * math.cos(angle), groove_radius * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_path = bl.wire()

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch.faces()[0]

groove_solid = sweep(sections=groove_face, path=helix_path)
solid_body = solid_body - groove_solid

cbore = Pos(counterbore_offset, 0, length / 2) * Cylinder(counterbore_diameter / 2.0, counterbore_depth)
thru = Pos(counterbore_offset, 0, 0) * Cylinder(through_hole_diameter / 2.0, length)
solid_body = solid_body - cbore - thru

part = solid_body
part.name = "hollow_cylinder_with_helical_groove"
export_step(part, "output.step")