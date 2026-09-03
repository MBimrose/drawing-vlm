from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
rib_height = 3.0
rib_width = 5.0
blind_hole_diameter = 6.0
blind_hole_depth = 6.0
blind_hole_count = 6
blind_hole_radius = (outer_diameter/2 + inner_diameter/2)/2
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((inner_diameter/2, 0), (outer_diameter/2, 0))
            Line((outer_diameter/2, 0), (outer_diameter/2, thickness))
            Line((outer_diameter/2, thickness), (inner_diameter/2, thickness))
            Line((inner_diameter/2, thickness), (inner_diameter/2, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

with BuildPart() as rib_p:
    with BuildSketch(Plane.XZ) as rib_sk:
        with BuildLine() as rib_bl:
            Line((inner_diameter/2 + rib_width, 0), (inner_diameter/2 + rib_width, rib_height))
            Line((inner_diameter/2 + rib_width, rib_height), (inner_diameter/2, rib_height))
            Line((inner_diameter/2, rib_height), (inner_diameter/2, 0))
            Line((inner_diameter/2, 0), (inner_diameter/2 + rib_width, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = solid_body + rib_p.part

for i in range(blind_hole_count):
    angle = math.radians(i * 360.0 / blind_hole_count)
    px = blind_hole_radius * math.cos(angle)
    py = blind_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

part = solid_body
part.name = "ring_with_rib_and_holes"
export_step(part, "output.step")