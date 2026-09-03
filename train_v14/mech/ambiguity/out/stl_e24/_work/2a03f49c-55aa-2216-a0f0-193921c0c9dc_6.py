from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_length = 60.0
slot_width = 5.0
hole_diameter = 5.0
hole_offset = 12.0
fillet_radius = 4.0
chamfer_distance = 0.5
boss_diameter = 20.0
boss_height = 5.0
rib_width = 5.0
rib_length = 30.0
rib_height = 2.0
counterbore_diameter = 10.0
counterbore_depth = 2.0
pocket_width = 20.0
pocket_length = 30.0
pocket_depth = 3.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2)
slot_solid = Pos(0, 0, -plate_thickness) * slot_bp.part
solid_body = solid_body - slot_solid

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

rib = Pos(-plate_length/2 + rib_length/2 + 10, 0, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(-plate_length/2 + pocket_length/2 + 10, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "plate_with_features"
export_step(part, "output.step")