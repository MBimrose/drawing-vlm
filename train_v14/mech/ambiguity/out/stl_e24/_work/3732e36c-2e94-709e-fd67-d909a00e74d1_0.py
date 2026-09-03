from build123d import *
import math

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 4.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_depth_cut = 2.0
slot_length = 30.0
slot_width = 8.0
slot_spacing = 30.0
hole_diameter = 4.0
hole_pattern_radius = 20.0
chamfer_size = 0.5
fillet_radius = 0.4

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = chamfer(solid_body.edges(), chamfer_size)

pocket = Pos(0, 0, plate_thickness - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - pocket

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2)
slot_solid = slot_bp.part

for y in [-slot_spacing/2, slot_spacing/2]:
    solid_body = solid_body - Pos(0, y, -plate_thickness) * slot_solid

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_pockets_slots_holes"
export_step(part, "output.step")