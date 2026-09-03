from build123d import *

bar_radius = 5
bar_length = 60
hole_diameter = 6
tab_width = 12
tab_height = 8
tab_thickness = 4
tab_hole_diameter = 4
tab_hole_offset = 2
chamfer_distance = 0.5
slot_length = 30
slot_width = 8
slot_depth = 6

with BuildPart() as p:
    with BuildSketch(Plane.YZ) as s:
        Circle(bar_radius)
    extrude(amount=bar_length)

solid_body = p.part
solid_body = solid_body - Pos(bar_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, bar_length + 10)

tab = Pos(bar_length, 0, 0) * Box(tab_thickness, tab_width, tab_height)
tab = chamfer(tab.edges().filter_by(Axis.Z), chamfer_distance)
solid_body = solid_body + tab

tab_hole_x = bar_length + tab_thickness/2 - tab_hole_offset
solid_body = solid_body - Pos(tab_hole_x, 0, 0) * Rot(0, 90, 0) * Cylinder(tab_hole_diameter/2, tab_thickness + 10)

slot = Pos(bar_length/2, 0, 0) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot

part = solid_body
part.name = "bar_with_tab_and_slot"
export_step(part, "output.step")