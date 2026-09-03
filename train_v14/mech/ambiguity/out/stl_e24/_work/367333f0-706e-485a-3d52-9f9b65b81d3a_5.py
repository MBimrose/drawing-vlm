from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_depth_cut = 2.5
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset_x = 15.0
hole_offset_y = 10.0
slot_width = 20.0
slot_depth = 4.0
slot_offset = 25.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

pocket = Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth_cut/2) * pocket

hole_positions = [
    (-plate_width/2 + hole_offset_x, -plate_depth/2 + hole_offset_y),
    ( plate_width/2 - hole_offset_x, -plate_depth/2 + hole_offset_y),
    (-plate_width/2 + hole_offset_x,  plate_depth/2 - hole_offset_y),
    ( plate_width/2 - hole_offset_x,  plate_depth/2 - hole_offset_y),
]
for x, y in hole_positions:
    csk = CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid_body = solid_body - Pos(x, y, plate_thickness) * csk

slot1 = Box(slot_width, slot_depth, plate_thickness)
solid_body = solid_body - Pos(0, slot_offset, plate_thickness/2) * slot1
slot2 = Box(slot_width, slot_depth, plate_thickness)
solid_body = solid_body - Pos(0, -slot_offset, plate_thickness/2) * slot2

part = solid_body
part.name = "plate_with_pockets_holes_slots"
export_step(part, "output.step")