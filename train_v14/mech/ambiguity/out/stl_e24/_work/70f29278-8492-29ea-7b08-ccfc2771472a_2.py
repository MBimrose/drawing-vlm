from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_length = 60.0
slot_width = 8.0
slot_fillet_radius = 2.0
boss_diameter = 12.0
boss_height = 6.0
boss_offset_x = 30.0
hole_diameter = 3.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
rib_width = 6.0
rib_height = 4.0
rib_offset_y = 5.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
pocket_offset_x = -20.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = slot_bp.part
slot_solid = Pos(0, 0, -plate_thickness/2) * slot_solid
solid_body = solid_body - slot_solid

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
slot_edges = top_face.edges().filter_by(Axis.Y)
solid_body = fillet(slot_edges, slot_fillet_radius)

boss_solid = Cylinder(boss_diameter/2, boss_height)
boss_solid = Pos(boss_offset_x, 0, plate_thickness/2 + boss_height/2) * boss_solid
solid_body = solid_body + boss_solid

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Cylinder(hole_diameter/2, 100)
        hole = Pos(x, y, 0) * hole
        solid_body = solid_body - hole

rib_solid = Box(rib_width, plate_width - 2*rib_offset_y, rib_height)
rib_solid = Pos(0, 0, -plate_thickness/2 - rib_height/2) * rib_solid
solid_body = solid_body + rib_solid

pocket_solid = Box(pocket_length, pocket_width, pocket_depth)
pocket_solid = Pos(pocket_offset_x, 0, -plate_thickness/2 + pocket_depth/2) * pocket_solid
solid_body = solid_body - pocket_solid

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
boss_edges = top_face.edges()
solid_body = chamfer(boss_edges, chamfer_size)

part = solid_body
part.name = "plate_with_slot_boss_holes"
export_step(part, "output.step")