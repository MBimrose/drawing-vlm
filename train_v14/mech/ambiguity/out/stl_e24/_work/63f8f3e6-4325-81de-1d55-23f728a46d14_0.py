from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 2.0
corner_radius = 15.0
tab_width = 20.0
tab_height = 10.0
tab_offset = 5.0
hole_diameter = 4.0
hole_offset = 10.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (plate_width, 0))
            l2 = Line(l1 @ 1, (plate_width, plate_depth - corner_radius))
            arc = RadiusArc(l2 @ 1, (plate_width - corner_radius, plate_depth), corner_radius)
            l3 = Line(arc @ 1, (0, plate_depth))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

tab = Pos(-tab_width/2 + tab_offset, plate_depth/2, plate_thickness/2) * Box(tab_width, tab_height, plate_thickness)
solid_body = solid_body + tab

hole_center_x = plate_width - hole_offset
hole_center_y = plate_depth - hole_offset
hole = Pos(hole_center_x, hole_center_y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness * 2)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_tab_and_hole"
export_step(part, "output.step")