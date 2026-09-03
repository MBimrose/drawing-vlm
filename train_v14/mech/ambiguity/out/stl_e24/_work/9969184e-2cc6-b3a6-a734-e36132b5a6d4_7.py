from build123d import *
import math

outer_diameter = 40.0
inner_diameter = 20.0
length = 80.0
groove_width = 4.0
groove_depth = 2.0
groove_turns = 3
hole_diameter = 6.0
hole_offset = 12.0
hole_center_z = length / 2.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length)
solid_body = solid_body - Cylinder(inner_radius, length)

solid_body = solid_body - Pos(hole_offset, 0, hole_center_z - length/2) * Cylinder(hole_diameter/2, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

num_points = 200
helix_points = []
for i in range(num_points):
    t = i / (num_points - 1)
    z = t * length
    angle = 2 * math.pi * groove_turns * t
    x = (outer_radius - groove_depth / 2.0) * math.cos(angle)
    y = (outer_radius - groove_depth / 2.0) * math.sin(angle)
    helix_points.append(Vector(x, y, z))

with BuildLine() as bl:
    Spline(*helix_points)
helix_path = bl.line

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch

groove_solid = sweep(sections=groove_face, path=helix_path)
solid_body = solid_body - groove_solid

part = solid_body
part.name = "helical_groove_shaft"
export_step(part, "output.step")