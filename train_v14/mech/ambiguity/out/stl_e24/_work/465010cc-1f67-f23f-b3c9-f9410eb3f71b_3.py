from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 12.0
corner_fillet_radius = 5.0
slot_length = 40.0
slot_width = 8.0
slot_spacing = 20.0
hole_diameter = 6.0
hole_offset = 15.0
boss_diameter = 20.0
boss_height = 8.0
boss_offset_x = 15.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)

solid_body = p.part

top_right_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-1:]
solid_body = fillet(top_right_edges, corner_fillet_radius)

for y in [-slot_spacing/2, slot_spacing/2]:
    slot = Pos(0, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
    solid_body = solid_body - slot

for x, y in [(-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
             (plate_width/2 - hole_offset, plate_depth/2 - hole_offset)]:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

boss_x = plate_width/2 - boss_offset_x
boss = Pos(boss_x, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "plate_with_slots_holes_boss"
export_step(part, "output.step")