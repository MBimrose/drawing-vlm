from build123d import *
import math

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
tube_length = 80.0
groove_width = 2.0
groove_depth = 1.0
helix_pitch = 10.0
hole_diameter = 4.0
hole_count = 8
hole_angle_step = 360.0 / hole_count

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=tube_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

helix_radius = outer_radius - groove_depth / 2
num_points = 200
helix_points = []
for i in range(num_points):
    t = i / (num_points - 1)
    angle = 2 * math.pi * (tube_length / helix_pitch) * t
    z = tube_length * t
    x = helix_radius * math.cos(angle)
    y = helix_radius * math.sin(angle)
    helix_points.append(Vector(x, y, z))

with BuildLine() as bl:
    Spline(*helix_points)
helix_path = bl.wire()

with BuildSketch(Plane.XZ) as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch

groove_solid = sweep(sections=groove_face, path=helix_path)
solid_body = solid_body - groove_solid

for i in range(hole_count):
    angle_deg = i * hole_angle_step
    angle_rad = math.radians(angle_deg)
    x = (outer_radius - wall_thickness / 2) * math.cos(angle_rad)
    y = (outer_radius - wall_thickness / 2) * math.sin(angle_rad)
    hole = Pos(x, y, tube_length / 2) * Rot(0, 0, angle_deg) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, wall_thickness + 1)
    solid_body = solid_body - hole

part = solid_body
part.name = "helical_groove_tube"
export_step(part, "output.step")