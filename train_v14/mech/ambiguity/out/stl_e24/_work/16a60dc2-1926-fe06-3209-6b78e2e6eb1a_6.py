from build123d import *

knob_diameter = 60.0
knob_thickness = 15.0
central_hole_diameter = 12.0
central_hole_depth = 10.0
rib_width = 6.0
rib_height = 8.0
rib_thickness = 4.0
rib_count = 4
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(knob_diameter / 2)
    extrude(amount=knob_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, knob_thickness - central_hole_depth / 2) * Cylinder(central_hole_diameter / 2, central_hole_depth)

mount_points = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, knob_thickness / 2) * Cylinder(mount_hole_diameter / 2, knob_thickness)

rib_center_x = knob_diameter / 2 - rib_thickness / 2
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(rib_center_x, 0, knob_thickness / 2) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "knob_with_ribs"
export_step(part, "output.step")