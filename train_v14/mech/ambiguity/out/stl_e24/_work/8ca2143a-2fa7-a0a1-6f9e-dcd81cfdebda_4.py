from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
dovetail_width = 10.0
dovetail_depth = 6.0
dovetail_angle = 30.0
hole_diameter = 5.0
hole_offset = 30.0
rib_height = 4.0
rib_thickness = 2.0
rib_width = 12.0
chamfer_size = 0.2

base = Box(jaw_length, jaw_width, jaw_thickness)
rib = Pos(0, 0, jaw_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = base + rib

hole_x = -jaw_length/2 + hole_offset
hole = Pos(hole_x, -jaw_width/2 + jaw_thickness/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, jaw_thickness)
solid_body = solid_body - hole

with BuildPart() as dovetail_bp:
    with BuildSketch(Plane.YZ.offset(jaw_length/2)) as sk:
        with BuildLine() as bl:
            Polyline((0, -dovetail_width/2), (dovetail_depth, -dovetail_width/2),
                     (dovetail_depth, dovetail_width/2), (0, dovetail_width/2), close=True)
        make_face()
    extrude(amount=-dovetail_depth)
solid_body = solid_body - dovetail_bp.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "jaw_with_dovetail"
export_step(part, "output.step")