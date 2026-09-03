from build123d import *

base_length = 80.0
base_width = 20.0
base_thickness = 8.0
tab_length = 20.0
tab_width = 10.0
slot_width = 2.0
slot_depth = 6.0
hole_diameter = 4.0
cbore_diameter = 6.1
cbore_depth = 4.0
chamfer_size = 0.2

base = Box(base_length, base_width, base_thickness)
tab = Pos(base_length/2, 0, 0) * Box(tab_length, tab_width, base_thickness)
solid_body = base + tab

slot_cut = Pos(base_length/2 + tab_length/4, 0, 0) * Box(slot_width, slot_depth, base_thickness)
solid_body = solid_body - slot_cut

hole_positions = [(-base_length/3, -base_width/4), (base_length/3, -base_width/4)]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, base_thickness/2) * CounterBoreHole(hole_diameter/2, cbore_diameter/2, cbore_depth, base_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_tab"
export_step(part, "output.step")