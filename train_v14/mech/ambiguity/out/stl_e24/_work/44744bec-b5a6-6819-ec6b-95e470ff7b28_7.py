from build123d import *

width = 70.0
depth = 30.0
thickness = 5.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_recess = 2.0
hole_diameter = 3.0
countersink_diameter = 5.0
countersink_angle = 82.0
hole_spacing = 20.0
chamfer_size = 0.5

solid_body = Box(width, depth, thickness)
pocket = Pos(0, 0, thickness/2 - pocket_recess/2) * Box(pocket_width, pocket_depth, pocket_recess)
solid_body = solid_body - pocket

for x in [-hole_spacing, 0, hole_spacing]:
    csk = Pos(x, 0, thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, thickness, countersink_angle)
    solid_body = solid_body - csk

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")