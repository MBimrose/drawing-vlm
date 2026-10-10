from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
rib_height = 6.0
rib_base = 10.0
rib_thickness = 3.0
hole_diameter = 8.0
hole_offset_x = 15.0
hole_offset_y = 0.0
fillet_radius = 1.0
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = 4.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ.offset(-bracket_width/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-rib_base/2, 0), (rib_base/2, 0))
            l2 = Line(l1@1, (0, rib_height))
            l3 = Line(l2@1, (-rib_base/2, 0))
        make_face()
    extrude(amount=bracket_thickness)
rib = rib_bp.part

result = base + rib

result = result - Pos(hole_offset_x, hole_offset_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 10)

result = result - Pos(0, bracket_width/2 - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket"
export_step(part, "output.step")