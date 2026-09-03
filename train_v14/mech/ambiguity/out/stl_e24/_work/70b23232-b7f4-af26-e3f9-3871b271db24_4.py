from build123d import *
import math

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
groove_width = 5.0
groove_depth = 2.0
groove_length = 40.0
groove_turns = 2.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_count = 3
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

helix_radius = outer_radius - groove_depth / 2
helix_pts = []
for i in range(200):
    t = i / 199
    angle = 2 * math.pi * groove_turns * t
    z = groove_length * t
    helix_pts.append(Vector(helix_radius * math.cos(angle), helix_radius * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_path = bl.wire()

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch.faces()[0]

groove_solid = sweep(sections=groove_face, path=helix_path)
solid_body = solid_body - groove_solid

for i in range(hole_count):
    angle = i * 360.0 / hole_count
    rad = math.radians(angle)
    x = (outer_radius - wall_thickness / 2) * math.cos(rad)
    y = (outer_radius - wall_thickness / 2) * math.sin(rad)
    hole = Pos(x, y, length / 2) * Rot(0, 90, angle) * Cylinder(hole_diameter / 2, wall_thickness + 1)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_groove_and_holes"
export_step(part, "output.step")