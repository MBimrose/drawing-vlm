from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 5.0
wall_thickness = 3.0
pocket_depth = 3.0
boss_diameter = 20.0
boss_height = 3.0
chamfer_distance = 0.5
hole_diameter = 5.0
hole_offset = 10.0
rib_width = 2.0
rib_height = 2.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

pocket_w = plate_width - 2 * wall_thickness
pocket_h = plate_height - 2 * wall_thickness
pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket

boss = Pos(0, 0, plate_thickness - pocket_depth + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_height/2 + hole_offset),
    (plate_width/2 - hole_offset, -plate_height/2 + hole_offset),
    (-plate_width/2 + hole_offset, plate_height/2 - hole_offset),
    (plate_width/2 - hole_offset, plate_height/2 - hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
    solid_body = solid_body - hole

rib_count = int((plate_width - 2 * wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -plate_width/2 + wall_thickness + i * rib_spacing
    rib = Pos(x_pos, 0, plate_thickness - pocket_depth + rib_height/2) * Box(rib_width, plate_height - 2 * wall_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_boss_holes_ribs"
export_step(part, "output.step")