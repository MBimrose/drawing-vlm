from build123d import *

panel_width = 100.0
panel_height = 70.0
panel_thickness = 4.0
notch_width = 15.0
notch_height = 10.0
pocket_width = 30.0
pocket_height = 20.0
hole_diameter = 5.5
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 4
slot_length = 60.0
slot_width = 5.0
chamfer_dist = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as bl:
            Polyline(
                (-panel_width/2, -panel_height/2),
                (panel_width/2, -panel_height/2),
                (panel_width/2, panel_height/2 - notch_height),
                (panel_width/2 - notch_width, panel_height/2 - notch_height),
                (panel_width/2 - notch_width, panel_height/2),
                (-panel_width/2, panel_height/2),
                close=True
            )
        make_face()
    extrude(amount=panel_thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, panel_thickness/2) * Box(pocket_width, pocket_height, panel_thickness)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = i * hole_spacing_x
        y = j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, panel_thickness/2) * Cylinder(hole_diameter/2, panel_thickness)

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=panel_thickness)
slot_solid = Pos(0, -panel_height/4, 0) * slot_p.part
solid_body = solid_body - slot_solid

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

part = solid_body
part.name = "panel_with_notch_pocket_holes_slot"
export_step(part, "output.step")