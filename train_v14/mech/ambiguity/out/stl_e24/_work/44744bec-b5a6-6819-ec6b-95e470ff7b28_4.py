from build123d import *
import math

plate_width = 70.0
plate_depth = 30.0
plate_thickness = 5.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_depth_cut = 2.0
hole_diameter = 3.0
countersink_diameter = 5.0
countersink_angle = 82.0
hole_spacing = 20.0
chamfer_size = 0.5
rib_height = 2.0
rib_width = 5.0
rib_length = plate_width - 10.0

solid_body = Box(plate_width, plate_depth, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - pocket

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    hole = Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_rib_holes"
export_step(part, "output.step")