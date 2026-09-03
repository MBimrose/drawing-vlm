from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
taper_length = 20.0
taper_width_end = 10.0
slot_width = 2.0
slot_length = 60.0
slot_depth = lever_thickness / 2
hole_diameter = 4.0
hole_spacing = 12.0
hole_offset = 15.0
chamfer_dist = 1.0
rib_width = 5.0
rib_depth = 8.0
rib_height = 2.0
pocket_width = 8.0
pocket_depth = 5.0
pocket_height = 3.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (lever_length, 0), (lever_length, taper_width_end),
                     (lever_length - taper_length, lever_width), (0, lever_width), close=True)
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part

slot_box = Pos(lever_length/2, lever_width/2, lever_thickness - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot_box

for i in range(3):
    hx = hole_offset + i * hole_spacing
    hy = lever_width / 2
    solid_body = solid_body - Pos(hx, hy, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness)

rib_box = Pos(lever_length/2, lever_width/2, lever_thickness - rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body - rib_box

pocket_box = Pos(lever_length/4, lever_width/2, lever_thickness - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket_box

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-1:]
solid_body = chamfer(chamfer_edges, chamfer_dist)

part = solid_body
part.name = "lever"
export_step(part, "output.step")