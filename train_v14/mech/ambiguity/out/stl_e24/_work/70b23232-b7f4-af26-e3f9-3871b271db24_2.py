from build123d import *
import math

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
groove_width = 5.0
groove_depth = 2.0
groove_pitch = 20.0
hole_diameter = 4.0
hole_count = 5
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

helix_radius = outer_radius - groove_depth / 2
num_points = 200
helix_points = []
for i in range(num_points):
    t = i / (num_points - 1)
    angle = 2 * math.pi * (length / groove_pitch) * t
    z = length * t
    x = helix_radius * math.cos(angle)
    y = helix_radius * math.sin(angle)
    helix_points.append(Vector(x, y, z))

with BuildLine() as bl:
    Spline(*helix_points)
helix_path = bl.line

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch.faces()[0]

groove_solid = sweep(sections=groove_face, path=helix_path)
solid_body = solid_body - groove_solid

hole_radius = hole_diameter / 2
hole_center_radius = outer_radius - wall_thickness / 2
for i in range(hole_count):
    angle = 2 * math.pi * i / hole_count
    x = hole_center_radius * math.cos(angle)
    y = hole_center_radius * math.sin(angle)
    hole = Pos(x, y, length / 2) * Rot(0, 90, math.degrees(angle)) * Cylinder(hole_radius, wall_thickness + 1)
    solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_helical_groove"
export_step(part, "output.step")