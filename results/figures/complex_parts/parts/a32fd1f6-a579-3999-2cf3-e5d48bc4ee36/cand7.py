from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 20.0
shaft_base_radius = 20.0
shaft_top_radius = 6.0
shaft_length = 30.0
hole_diameter = 6.0
hole_offset_x = 30.0
hole_offset_y = 15.0
chamfer_size = 1.0
slot_width = 4.0
slot_depth = 2.0
pocket_width = 12.0
pocket_depth = 4.0
pocket_offset = 10.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
shaft = Pos(0, 0, plate_thickness/2 + boss_height + shaft_length/2) * Cone(shaft_base_radius, shaft_top_radius, shaft_length)
result = base + boss + shaft

hole_h = plate_thickness + boss_height + shaft_length + 20
for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, hole_h)

slot = Pos(0, 0, plate_thickness/2 + boss_height + shaft_length - slot_depth/2) * Box(slot_width, slot_depth, slot_depth)
result = result - slot

pocket = Pos(pocket_offset, 0, plate_thickness/2 + boss_height + shaft_length - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
result = result - pocket

edges = result.edges().filter_by(GeomType.CIRCLE)
target_z = plate_thickness/2 + boss_height
closest = min(edges, key=lambda e: abs(e.center().Z - target_z))
result = chamfer([closest], chamfer_size)

part = result
part.name = "plate_with_boss_shaft"
export_step(part, "output.step")