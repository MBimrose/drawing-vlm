from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
rib_height = 12.0
rib_base = 10.0
hole_diameter = 8.0
hole_offset = 15.0
fillet_radius = 1.0
slot_length = 20.0
slot_width = 6.0

base = Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ.offset(-bracket_width/2)) as sk:
        with BuildLine() as bl:
            Polyline((-rib_base/2, -bracket_thickness/2), (rib_base/2, -bracket_thickness/2), (0, -bracket_thickness/2 + rib_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
rib = rib_bp.part

result = base + rib
result = result - Pos(hole_offset, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)
result = result - Pos(0, bracket_width/2 - slot_width/2, 0) * Box(slot_length, slot_width, bracket_thickness * 2)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")