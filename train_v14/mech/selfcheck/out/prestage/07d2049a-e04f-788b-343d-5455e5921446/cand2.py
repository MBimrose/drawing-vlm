from build123d import *
import math

hub_diameter = 30.0
hub_length = 20.0
flange_diameter = 80.0
flange_thickness = 25.0
bore_diameter = 12.0
fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_count = 2
mount_hole_radius = (flange_diameter/2) - 10.0

hub_radius = hub_diameter/2
flange_radius = flange_diameter/2
bore_radius = bore_diameter/2
total_length = hub_length + flange_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0,0), (hub_radius, 0), (hub_radius, hub_length), (flange_radius, hub_length), (flange_radius, total_length), (0, total_length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

bore = Pos(0, 0, total_length/2) * Cylinder(bore_radius, total_length)
solid_body = solid_body - bore

for i in range(mount_hole_count):
    angle = math.radians(45 + i * 180.0)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    hole = Pos(px, py, total_length/2) * Cylinder(mount_hole_diameter/2, total_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "hub_flange"
export_step(part, "output.step")