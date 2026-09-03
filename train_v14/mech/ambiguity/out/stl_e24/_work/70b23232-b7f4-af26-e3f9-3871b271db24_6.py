from build123d import *
import math

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
groove_width = 2.0
groove_depth = 2.0
groove_pitch = 12.0
hole_diameter = 4.0
hole_count = 5

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

helix_radius = inner_radius - groove_depth / 2
num_pts = 200
helix_pts = []
for i in range(num_pts):
    t = i / (num_pts - 1)
    angle = 2 * math.pi * (length / groove_pitch) * t
    z = length * t
    helix_pts.append(Vector(helix_radius * math.cos(angle), helix_radius * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_wire = bl.wire()

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch

groove_solid = sweep(sections=groove_face, path=helix_wire)
solid_body = solid_body - groove_solid

hole_radius = hole_diameter / 2
hole_length = wall_thickness + 1.0
for i in range(hole_count):
    angle = i * 360.0 / hole_count
    rad = math.radians(angle)
    px = (outer_radius - wall_thickness / 2) * math.cos(rad)
    py = (outer_radius - wall_thickness / 2) * math.sin(rad)
    hole = Pos(px, py, 0) * Rot(0, 90, angle) * Cylinder(hole_radius, hole_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_helical_groove"
export_step(part, "output.step")