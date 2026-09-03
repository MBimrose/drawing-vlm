from build123d import *

outer_length = 60.0
outer_width = 40.0
outer_height = 30.0
wall_thickness = 3.0
slot_width = 8.0
slot_height = 20.0
slot_offset_z = 5.0
chamfer_size = 0.5
center_hole_diameter = 5.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

slot_z = slot_offset_z + slot_height/2
slot_box = Box(slot_width, wall_thickness, slot_height)
base = base - Pos(outer_length/2 - wall_thickness/2, 0, slot_z) * slot_box
base = base - Pos(-outer_length/2 + wall_thickness/2, 0, slot_z) * slot_box
base = base - Pos(0, outer_width/2 - wall_thickness/2, slot_z) * slot_box
base = base - Pos(0, -outer_width/2 + wall_thickness/2, slot_z) * slot_box

base = base - Pos(0, 0, outer_height/2) * Cylinder(center_hole_diameter/2, outer_height)

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "hollow_box_with_slots"
export_step(part, "output.step")