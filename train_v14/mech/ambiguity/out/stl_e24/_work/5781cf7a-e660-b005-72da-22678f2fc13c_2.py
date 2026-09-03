from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
dovetail_depth = 10.0
dovetail_width_top = 25.0
dovetail_width_bottom = 40.0
fillet_radius = 1.0
rib_width = 5.0
rib_height = 4.0
rib_spacing = 15.0
rib_depth = 2.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as dovetail_bp:
    with BuildSketch(Plane.XZ.offset(outer_width/2)) as dovetail_sk:
        with BuildLine() as dl:
            Polyline(
                (-dovetail_width_bottom/2, 0),
                (-dovetail_width_top/2, dovetail_depth),
                (dovetail_width_top/2, dovetail_depth),
                (dovetail_width_bottom/2, 0),
                close=True
            )
        make_face()
    extrude(amount=-outer_length)
solid_body = solid_body - dovetail_bp.part

rib_count = int((outer_length - 2 * wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, outer_height + rib_depth/2) * Box(rib_width, rib_height, rib_depth)
    solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), 0.5)

part = solid_body
part.name = "dovetail_box_with_ribs"
export_step(part, "output.step")