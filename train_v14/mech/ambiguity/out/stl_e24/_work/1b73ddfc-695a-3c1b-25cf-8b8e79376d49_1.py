from build123d import *

base_width = 60.0
base_depth = 40.0
base_thickness = 8.0
rib_width = 6.0
rib_depth = 4.0
rib_height = 3.0
rib_offset = 10.0
hole_diameter = 4.0
countersink_diameter = 5.0
countersink_depth = 2.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
rib1 = Pos(-base_width/2 + rib_offset, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
rib2 = Pos(base_width/2 - rib_offset, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = base + rib1 + rib2
hole = CounterSinkHole(hole_diameter/2, countersink_diameter/2, base_thickness)
solid_body = solid_body - hole
part = solid_body
part.name = "base_plate_with_ribs"
export_step(part, "output.step")