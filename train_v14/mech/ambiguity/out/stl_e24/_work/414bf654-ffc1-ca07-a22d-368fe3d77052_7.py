from build123d import *
import math

outer_radius = 20.0
wall_thickness = 2.0
inner_radius = outer_radius - wall_thickness
length = 70.0
groove_width = 5.0
groove_depth = 1.5
groove_pitch = 10.0
hole_diameter = 8.0
hole_spacing = 30.0
hole_offset = 15.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((outer_radius, 0), (outer_radius, length), (inner_radius, length), (inner_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

num_turns = length / groove_pitch
num_pts = 200
helix_pts = []
for i in range(num_pts + 1):
    t = i / num_pts
    angle = 2 * math.pi * num_turns * t
    z = length * t
    r = inner_radius - groove_depth / 2
    helix_pts.append(Vector(r * math.cos(angle), r * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_path = bl.line

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch

groove_solid = sweep(sections=groove_face, path=helix_path)
solid_body = solid_body - groove_solid

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, length)

solid_body = solid_body - Rot(90, 0, 0) * Cylinder(hole_diameter/2, length)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_holes"
export_step(part, "output.step")