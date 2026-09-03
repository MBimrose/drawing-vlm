from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
dovetail_depth = 15.0
dovetail_width_bottom = 40.0
dovetail_width_top = 20.0
fillet_radius = 1.0
rib_width = 5.0
rib_height = 4.0
rib_spacing = 15.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

with BuildPart() as dovetail_bp:
    with BuildSketch(Plane.XY.offset(wall_thickness)) as dovetail_sk:
        with BuildLine() as dl:
            Polyline((-dovetail_width_bottom/2, 0), (dovetail_width_bottom/2, 0),
                     (dovetail_width_top/2, outer_width), (-dovetail_width_top/2, outer_width), close=True)
        make_face()
    extrude(amount=dovetail_depth)
solid_body = solid_body - dovetail_bp.part

num_ribs = int((outer_length - 2*wall_thickness) // rib_spacing) + 1
for i in range(num_ribs):
    x = -outer_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x, 0, outer_height + wall_thickness/2) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "dovetail_box_with_ribs"
export_step(part, "output.step")