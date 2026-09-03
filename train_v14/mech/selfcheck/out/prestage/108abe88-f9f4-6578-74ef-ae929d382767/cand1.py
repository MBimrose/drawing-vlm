from build123d import *

beam_length = 80.0
beam_height = 30.0
flange_width = 50.0
flange_thickness = 12.0
web_thickness = 10.0
rib_width = 6.0
rib_height = 8.0
pocket_width = 30.0
pocket_depth = 6.0
pocket_length = 60.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_count = 5
chamfer_size = 1.0

web = Box(web_thickness, beam_height, beam_length)
flange = Pos(0, beam_height/2 + flange_thickness/2, 0) * Box(flange_width, flange_thickness, beam_length)
base = web + flange

rib = Pos(0, beam_height/2 + flange_thickness + rib_height/2, 0) * Box(rib_width, rib_height, beam_length)
base = base + rib

pocket = Pos(0, beam_height/2 + flange_thickness + rib_height - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_length)
base = base - pocket

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, beam_length + 20)
    base = base - hole

z_edges = base.edges().filter_by(Axis.Z)
sorted_edges = z_edges.sort_by(Axis.Y)
top_y = sorted_edges[-1].center().Y
bottom_y = sorted_edges[0].center().Y
chamfer_edges = [e for e in z_edges if abs(e.center().Y - top_y) < 0.1 or abs(e.center().Y - bottom_y) < 0.1]
base = chamfer(chamfer_edges, chamfer_size)

part = base
part.name = "I-beam_with_rib_pocket_holes"
export_step(part, "output.step")