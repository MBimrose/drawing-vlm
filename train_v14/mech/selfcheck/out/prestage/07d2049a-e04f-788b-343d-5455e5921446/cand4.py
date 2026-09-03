from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
collar_length = 40.0
shoulder_length = 15.0
fillet_radius = 3.0
central_hole_diameter = 12.0
mounting_hole_diameter = 5.0
mounting_hole_offset = 10.0
mounting_hole_angle = 45.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shoulder_radius, 0))
            l2 = Line(l1 @ 1, (shoulder_radius, shoulder_length))
            l3 = Line(l2 @ 1, (outer_radius, shoulder_length))
            l4 = Line(l3 @ 1, (outer_radius, collar_length))
            l5 = Line(l4 @ 1, (0, collar_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, collar_length * 2)

hole_radius = outer_radius - mounting_hole_offset
for i in range(2):
    angle = math.radians(mounting_hole_angle + i * 180.0)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mounting_hole_diameter / 2, collar_length * 2)

part = solid_body
part.name = "stepped_collar"
export_step(part, "output.step")