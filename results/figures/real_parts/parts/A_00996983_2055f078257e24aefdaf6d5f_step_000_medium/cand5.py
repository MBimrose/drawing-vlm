from build123d import *
import math

outer_diameter = 80.0
height = 30.0
wall_thickness = 5.0
slot_width = 5.0
slot_depth = wall_thickness
slot_count = 12
chamfer_size = 3.0
hex_flat_distance = 60.0
hex_height = 30.0
central_hole_diameter = 5.0

outer_radius = outer_diameter / 2.0
hex_radius = hex_flat_distance / (2 * math.cos(math.radians(30)))

solid_body = Cylinder(outer_radius, height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_width, slot_depth, height)
    solid_body = solid_body - slot

with BuildPart() as hex_bp:
    with BuildSketch(Plane.XY.offset(height / 2.0)) as hex_sk:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_height)
solid_body = solid_body + hex_bp.part

hole = Pos(0, 0, height / 2.0 + hex_height / 2.0) * Cylinder(central_hole_diameter / 2.0, height + hex_height + 20)
solid_body = solid_body - hole

part = solid_body
part.name = "slotted_cylinder_with_hex"
export_step(part, "output.step")