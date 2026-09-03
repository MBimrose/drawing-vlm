from build123d import *
import math

hub_diameter = 30.0
hub_height = 20.0
shoulder_diameter = 80.0
shoulder_height = 25.0
bore_diameter = 12.0
fillet_radius = 4.0
mount_hole_diameter = 5.0
mount_hole_angle = 45.0
mount_hole_radius = (shoulder_diameter/2) - 10.0
pocket_width = 10.0
pocket_depth = 5.0
pocket_offset = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (hub_diameter/2, 0))
            l2 = Line(l1@1, (hub_diameter/2, hub_height))
            l3 = Line(l2@1, (shoulder_diameter/2, hub_height))
            l4 = Line(l3@1, (shoulder_diameter/2, hub_height + shoulder_height))
            l5 = Line(l4@1, (0, hub_height + shoulder_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

total_height = hub_height + shoulder_height
solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(bore_diameter/2, total_height + 10)

for i in range(2):
    angle = math.radians(mount_hole_angle + i * 180.0)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height/2) * Cylinder(mount_hole_diameter/2, total_height + 10)

pocket = Pos(pocket_offset, 0, hub_height/2 - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "stepped_shaft_with_pocket"
export_step(part, "output.step")