from build123d import *
import math

block_length = 80.0
block_width = 80.0
block_thickness = 20.0
slot_width = 12.0
slot_height = 20.0
slot_depth = 10.0
hole_diameter = 4.5
countersink_diameter = 9.0
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 60.0
hole_edge_offset = 10.0
fillet_radius = 2.0
boss_radius = 8.0
boss_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

slot = Box(slot_width, slot_depth, slot_height)
solid_body = solid_body - Pos(0, block_width/2 - slot_depth/2, block_thickness/2) * slot

boss = Cylinder(boss_radius, boss_height)
solid_body = solid_body + Pos(0, 0, 0) * boss

csk_half_angle = math.radians(countersink_angle / 2)
csk_height = (countersink_diameter/2 - hole_diameter/2) / math.tan(csk_half_angle)

shaft = Cylinder(hole_diameter/2, block_thickness + 1)
csk_cone = Cone(hole_diameter/2, countersink_diameter/2, csk_height)
hole_tool = shaft + Pos(0, 0, block_thickness/2 - csk_height/2) * csk_cone

x_start = -block_length/2 + hole_edge_offset
x_positions = [x_start + i*hole_spacing_x for i in range(4)]
y_positions = [-hole_spacing_y/2, hole_spacing_y/2]
points = [(x, y) for y in y_positions for x in x_positions]

for x, y in points:
    solid_body = solid_body - Pos(x, y, 0) * hole_tool

part = solid_body
part.name = "block_with_slot_boss_and_holes"
export_step(part, "output.step")