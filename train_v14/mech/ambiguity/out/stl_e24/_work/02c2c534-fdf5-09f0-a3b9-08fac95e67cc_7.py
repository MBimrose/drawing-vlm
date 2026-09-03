from build123d import *
import math

hub_radius = 10.0
hub_height = 10.0
shaft_length = 60.0
shaft_start_radius = hub_radius
shaft_end_radius = 5.0
groove_width = 2.0
groove_depth = 3.0
groove_pitch = 10.0
num_grooves = 3
bore_diameter = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_start_radius, 0))
            l2 = Line(l1 @ 1, (shaft_start_radius, hub_height))
            l3 = Line(l2 @ 1, (shaft_end_radius, hub_height + shaft_length))
            l4 = Line(l3 @ 1, (0, hub_height + shaft_length))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(bore_diameter / 2, hub_height + shaft_length + 20)

total_height = hub_height + shaft_length
for i in range(num_grooves):
    angle_offset = i * 360.0 / num_grooves
    num_pts = 20
    pts = []
    for j in range(num_pts + 1):
        t = j / num_pts
        z = t * total_height
        radius = shaft_start_radius + (shaft_end_radius - shaft_start_radius) * t
        angle = t * 360.0 + angle_offset
        rad = math.radians(angle)
        x = radius * math.cos(rad)
        y = radius * math.sin(rad)
        pts.append(Vector(x, y, z))
    with BuildLine() as bl:
        Spline(*pts)
    path = bl.wire()
    with BuildSketch() as sk:
        Rectangle(groove_width, groove_depth)
    profile = sk.face()
    groove = sweep(sections=profile, path=path)
    solid_body = solid_body - groove

part = solid_body
part.name = "revolved_shaft_with_grooves"
export_step(part, "output.step")