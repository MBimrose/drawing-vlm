from build123d import *

outer_size = 80.0
wall_thickness = 5.0
length = 40.0
hole_diameter = 12.0
chamfer_size = 2.0
rib_thickness = 5.0

inner_size = outer_size - 2 * wall_thickness

outer = Box(outer_size, outer_size, length)
inner = Box(inner_size, inner_size, length)
base = outer - inner

hole = Rot(0, 90, 0) * Cylinder(hole_diameter / 2, outer_size)
base = base - hole

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

rib1 = Pos(0, 0, length / 2 - rib_thickness / 2) * Box(inner_size, rib_thickness, rib_thickness)
rib2 = Pos(0, 0, length / 2 - rib_thickness / 2) * Box(rib_thickness, inner_size, rib_thickness)

part = base + rib1 + rib2
part.name = "hollow_box_with_ribs"
export_step(part, "output.step")