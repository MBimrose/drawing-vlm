from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
rib_height = 2.0
rib_offset = 10.0
slot_length = 60.0
slot_width = 5.0
hole_diameter = 6.0
hole_offset = 12.0
chamfer_size = 0.5
boss_diameter = 15.0
boss_height = 8.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(plate_length - 2 * rib_offset, plate_width - 2 * rib_offset)
    extrude(amount=rib_height)

solid_body = p.part

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + rib_height + 10)
slot_cut = Pos(0, 0, -5) * slot_p.part
solid_body = solid_body - slot_cut

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

boss = Pos(0, 0, plate_thickness + rib_height + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "plate_with_rib_slot_holes_boss"
export_step(part, "output.step")