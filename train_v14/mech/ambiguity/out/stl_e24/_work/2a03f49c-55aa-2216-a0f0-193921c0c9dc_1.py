from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
corner_radius = 4.0
hole_diameter = 5.0
counterbore_diameter = 10.0
counterbore_depth = 2.0
hole_offset = 12.0
slot_width = 5.0
slot_length = 20.0
slot_offset = 10.0
rib_thickness = 3.0
rib_width = 10.0
rib_length = plate_length - 20.0
boss_diameter = 20.0
boss_height = 5.0
chamfer_size = 0.5
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0
pocket_offset_x = -plate_length/2 + 15.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

with BuildPart() as sp:
    with BuildSketch() as ss:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_tool = sp.part
solid_body = solid_body - Pos(-plate_length/2 + slot_offset, 0, 0) * slot_tool
solid_body = solid_body - Pos(plate_length/2 - slot_offset, 0, 0) * slot_tool

solid_body = solid_body + Pos(0, 0, -rib_thickness/2) * Box(rib_length, rib_width, rib_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(pocket_offset_x, 0, plate_thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_features"
export_step(part, "output.step")