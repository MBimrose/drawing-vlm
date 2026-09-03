from build123d import *
import math

rail_length = 80.0
rail_width = 20.0
rail_height = 10.0
wall_thickness = 2.0
v_groove_depth = 4.0
v_groove_angle = 60.0
chamfer_size = 0.5
hole_diameter = 4.0
hole_spacing = 30.0
rib_height = 2.0
rib_width = 6.0

v_groove_width = 2 * v_groove_depth * math.tan(math.radians(v_groove_angle / 2))

base = Box(rail_length, rail_width, rail_height)
rib = Pos(0, 0, rail_height/2 - rib_height/2) * Box(rail_length, rib_width, rib_height)
solid_body = base + rib

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            Polyline((-v_groove_width/2, rail_height/2), (0, rail_height/2 - v_groove_depth), (v_groove_width/2, rail_height/2), close=True)
        make_face()
    extrude(amount=rail_length)
groove = Pos(-rail_length/2, 0, 0) * gp.part
solid_body = solid_body - groove

x_edges = solid_body.edges().filter_by(Axis.X)
solid_body = chamfer(x_edges, chamfer_size)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, rail_height + 10)

part = solid_body
part.name = "rail_with_v_groove"
export_step(part, "output.step")