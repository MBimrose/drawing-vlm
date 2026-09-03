from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_thickness = 10.0
slot_length = 30.0
slot_width = 6.0
slot_offset_y = 5.0
hole_diameter = 4.5
hole_head_diameter = 8.6
hole_head_angle = 90.0
hole_spacing = 50.0
rib_height = 3.0
rib_width = 5.0
rib_spacing = 15.0
chamfer_size = 0.8

solid = Box(block_length, block_width, block_thickness)

slot = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, block_thickness + 0.1)
solid = solid - slot

csk_radius = hole_head_diameter / 2
csk_height = csk_radius / math.tan(math.radians(hole_head_angle / 2))
bore_radius = hole_diameter / 2

for x in [-hole_spacing/2, hole_spacing/2]:
    bore = Pos(x, 0, 0) * Cylinder(bore_radius, block_thickness + 0.1)
    csk = Pos(x, 0, -block_thickness/2 + csk_height/2) * Cone(csk_radius, 0.0, csk_height)
    solid = solid - (bore + csk)

rib_count = int((block_length - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x = -block_length/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(x, 0, -block_thickness/2 + rib_height/2) * Box(rib_width, block_width - 2*rib_spacing, rib_height)
    solid = solid + rib

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "block_with_slot_holes_ribs"
export_step(part, "output.step")