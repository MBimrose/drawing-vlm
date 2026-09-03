from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
taper_length = 20.0
taper_width_end = 10.0
groove_width = 2.0
groove_depth = 5.0
groove_length = 60.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_offset = 15.0
chamfer_size = 1.0
rib_width = 5.0
rib_height = 5.0
rib_length = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (lever_length, 0))
            l2 = Line(l1 @ 1, (lever_length, taper_width_end))
            l3 = Line(l2 @ 1, (lever_length - taper_length, lever_width))
            l4 = Line(l3 @ 1, (0, lever_width))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part

groove_box = Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - Pos(lever_length/2, lever_width/2, lever_thickness - groove_depth/2) * groove_box

for i in range(4):
    x = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, lever_width/2, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness)

rib_box = Box(rib_length, rib_width, rib_height)
solid_body = solid_body + Pos(lever_length/2, lever_width/2, rib_height/2) * rib_box

z_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)
solid_body = chamfer(z_edges[-2:], chamfer_size)

part = solid_body
part.name = "lever"
export_step(part, "output.step")