from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 20.0
length = 60.0
reduced_length = 30.0
hole_diameter = 6.0
hole_count = 6
fillet_radius = 2.0
hole_radius = (inner_diameter/2 + outer_diameter/2) / 2

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, -length/2), (outer_diameter/2, -length/2),
                     (outer_diameter/2, -reduced_length/2),
                     (inner_diameter/2, -reduced_length/2),
                     (inner_diameter/2, reduced_length/2),
                     (outer_diameter/2, reduced_length/2),
                     (outer_diameter/2, length/2),
                     (0, length/2), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, length)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "stepped_shaft_with_holes"
export_step(part, "output.step")