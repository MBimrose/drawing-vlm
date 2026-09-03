from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 6.0
blind_hole_count = 6
blind_hole_radius = (inner_diameter/2 + outer_diameter/2) / 2
pocket_diameter = 20.0
pocket_depth = 4.0
slot_width = 12.0
slot_height = 6.0
slot_offset = 15.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_diameter/2, 0), (inner_diameter/2, thickness))
            l2 = Line(l1@1, (outer_diameter/2, thickness))
            l3 = Line(l2@1, (outer_diameter/2, 0))
            l4 = Line(l3@1, (inner_diameter/2, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, thickness - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

for i in range(blind_hole_count):
    angle = math.radians(i * 360.0 / blind_hole_count)
    px = blind_hole_radius * math.cos(angle)
    py = blind_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

solid_body = solid_body - Pos(slot_offset, 0, thickness - thickness/4) * Box(slot_width, slot_height, thickness/2)

part = solid_body
part.name = "ring_with_pocket_holes_slot"
export_step(part, "output.step")