from build123d import *
import math

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
v_groove_depth = 4.0
v_groove_angle = 60.0
hole_diameter = 5.0
hole_offset_x = 30.0
hole_offset_z = 4.0
chamfer_size = 0.5
rib_height = 4.0
rib_width = 12.0
rib_thickness = 2.0

half_angle_rad = math.radians(v_groove_angle / 2.0)
v_groove_width = 2.0 * v_groove_depth * math.tan(half_angle_rad)

base = Box(jaw_length, jaw_width, jaw_thickness)

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (-v_groove_width/2, -v_groove_depth))
            l2 = Line(l1@1, (v_groove_width/2, -v_groove_depth))
            l3 = Line(l2@1, (0, 0))
        make_face()
    extrude(amount=jaw_thickness)
groove = Pos(jaw_length/2, jaw_width/2, 0) * gp.part
groove = chamfer(groove.edges(), chamfer_size)

result = base - groove

hole = Pos(-jaw_length/2 + hole_offset_x, -jaw_width/2 + jaw_thickness/2, hole_offset_z - jaw_thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, jaw_thickness)
result = result - hole

rib = Pos(0, 0, jaw_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
result = result + rib

part = result
part.name = "jaw_with_groove"
export_step(part, "output.step")