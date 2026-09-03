from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
rib_height = 6.0
rib_base = 10.0
hole_diameter = 8.0
hole_offset_x = 15.0
fillet_radius = 1.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 4.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-rib_base/2, 0), (rib_base/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
rib = Pos(0, bracket_width/2, 0) * rib_bp.part

result = base + rib

hole = Pos(hole_offset_x, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness * 2)
result = result - hole

pocket = Pos(0, bracket_width/2 - pocket_depth/2, bracket_thickness/2) * Box(pocket_length, pocket_depth, pocket_width)
result = result - pocket

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")