from build123d import *

plate_width = 70.0
plate_depth = 30.0
plate_thickness = 5.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_recess_depth = 2.0
hole_diameter = 3.0
csk_diameter = 5.0
csk_angle = 82.0
hole_spacing = 20.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_depth, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_recess_depth/2) * Box(pocket_width, pocket_depth, pocket_recess_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    csk = Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, csk_diameter/2, plate_thickness, csk_angle)
    solid_body = solid_body - csk

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")