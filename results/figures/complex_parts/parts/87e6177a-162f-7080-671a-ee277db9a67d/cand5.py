from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
central_hole_diameter = 20.0
central_hole_depth = 40.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_thickness = 2.0
rib_height = 8.0
rib_count = 6
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = solid_body - Pos(0, 0, height - central_hole_depth/2) * Cylinder(central_hole_diameter/2, central_hole_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

mount_radius = outer_radius - wall_thickness/2
for i in range(4):
    angle = math.radians(i * 90)
    px = mount_radius * math.cos(angle)
    py = mount_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, mount_hole_offset/2) * Cylinder(mount_hole_diameter/2, mount_hole_offset)

rib_radius = inner_radius - rib_thickness/2
for i in range(rib_count):
    angle = math.radians(i * 360 / rib_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    solid_body = solid_body + Pos(px, py, rib_height/2) * Cylinder(rib_thickness/2, rib_height)

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")