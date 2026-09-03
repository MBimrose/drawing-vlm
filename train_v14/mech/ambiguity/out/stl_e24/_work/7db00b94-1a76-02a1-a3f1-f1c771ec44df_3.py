from build123d import *
import math

block_width = 80.0
block_length = 80.0
block_thickness = 20.0
pocket_width = 12.0
pocket_length = 20.0
pocket_depth = 15.0
fillet_radius = 2.0
hole_diameter = 4.5
hole_depth = 12.0
countersink_angle = 90.0
countersink_depth = 2.5
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 30.0
edge_margin = 10.0
boss_radius = 8.0
boss_height = 5.0

solid = Box(block_width, block_length, block_thickness)
solid = fillet(solid.edges(), fillet_radius)

pocket = Pos(0, block_length/2 - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_length)
solid = solid - pocket

boss = Pos(0, 0, -block_thickness/2) * Cylinder(boss_radius, boss_height)
solid = solid + boss

csk_radius = hole_diameter/2 + countersink_depth * math.tan(math.radians(countersink_angle/2))
hole_tool = Cylinder(hole_diameter/2, hole_depth) + Cone(hole_diameter/2, csk_radius, countersink_depth)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -block_width/2 + edge_margin + i * hole_spacing_x
        y = -block_length/2 + edge_margin + j * hole_spacing_y
        solid = solid - Pos(x, y, block_thickness/2 - hole_depth/2) * hole_tool

part = solid
part.name = "block_with_pocket_boss_and_holes"
export_step(part, "output.step")