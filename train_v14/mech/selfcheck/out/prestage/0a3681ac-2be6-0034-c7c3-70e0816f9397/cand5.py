from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
rib_height = 6.0
rib_base = 10.0
hole_diameter = 8.0
hole_offset_from_right = 15.0
fillet_radius = 1.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_offset_from_left = 10.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-rib_base/2, 0), (rib_base/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
rib = rib_bp.part

result = base + rib

hole_x = bracket_length/2 - hole_offset_from_right
result = result - Pos(hole_x, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness * 2)

pocket_x = -bracket_length/2 + pocket_offset_from_left + pocket_width/2
pocket = Pos(pocket_x, bracket_width/2 - bracket_thickness/2, 0) * Box(pocket_width, bracket_thickness, pocket_depth)
result = result - pocket

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")