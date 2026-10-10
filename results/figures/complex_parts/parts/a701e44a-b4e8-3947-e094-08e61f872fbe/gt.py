from build123d import *
import math

frame_length = 80.0
frame_width = 40.0
frame_thickness = 8.0
tab_width = 15.0
tab_height = 30.0
tab_thickness = frame_thickness
hole_diameter = 6.0
csk_diameter = 10.0
csk_angle = 82.0
fillet_radius = 4.0
chamfer_dist = 1.0
rib_width = 4.0
rib_height = 2.0
rib_spacing = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (frame_length, 0), (frame_length, frame_width),
                (frame_length - tab_width, frame_width),
                (frame_length - tab_width, frame_width + tab_height),
                (frame_length - tab_width - tab_thickness, frame_width + tab_height),
                (frame_length - tab_width - tab_thickness, frame_width),
                (0, frame_width), close=True)
        make_face()
    extrude(amount=frame_thickness)

solid_body = p.part
z_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)
solid_body = fillet(z_edges[-2:], fillet_radius)

inner_box = Pos(frame_thickness, frame_thickness, frame_thickness/2) * Box(
    frame_length - 2*frame_thickness, frame_width - 2*frame_thickness, frame_thickness)
solid_body = solid_body - inner_box

num_ribs = int((frame_length - 2*frame_thickness) // rib_spacing)
for i in range(num_ribs):
    x = frame_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x, frame_width/2, rib_height/2) * Box(rib_width, frame_width - 2*frame_thickness, rib_height)
    solid_body = solid_body + rib

csk_depth = (csk_diameter - hole_diameter) / (2 * math.tan(math.radians(csk_angle/2)))
hole_center_x = frame_length - tab_width/2 - tab_thickness/2
hole_center_y = frame_width + tab_height/2

csk_cone = Pos(hole_center_x, hole_center_y, frame_thickness) * Cone(csk_diameter/2, hole_diameter/2, csk_depth)
solid_body = solid_body - csk_cone

through_hole = Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter/2, frame_thickness*2)
solid_body = solid_body - through_hole

max_x_edges = solid_body.edges().sort_by(Axis.X)[-1:]
solid_body = chamfer(max_x_edges, chamfer_dist)
max_y_edges = solid_body.edges().sort_by(Axis.Y)[-1:]
solid_body = chamfer(max_y_edges, chamfer_dist)

part = solid_body
part.name = "frame_with_tab"
export_step(part, OUTPUT_PATH)