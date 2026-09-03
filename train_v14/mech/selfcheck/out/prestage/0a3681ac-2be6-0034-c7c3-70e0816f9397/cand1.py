from build123d import *

bracket_length = 70
bracket_width = 30
bracket_thickness = 8
rib_height = 6
rib_base = 10
hole_diameter = 8
hole_offset_x = 20
fillet_radius = 1
notch_width = 20
notch_depth = 4

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-rib_base/2, 0), (rib_base/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
rib = Pos(0, bracket_width/2, 0) * rib_bp.part

result = base + rib

notch = Pos(0, bracket_width/2 - bracket_thickness/2, 0) * Box(notch_width, bracket_thickness, notch_depth)
result = result - notch

result = result - Pos(hole_offset_x, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness * 2)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")