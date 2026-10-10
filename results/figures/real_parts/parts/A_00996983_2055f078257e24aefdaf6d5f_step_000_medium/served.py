from build123d import *
import math

# ---- Dimensions (mm) ----
outer_radius = 40.0          # gear envelope radius (pitch circle)
num_teeth = 12               # number of external teeth
tooth_depth = 6.0            # radial tooth depth
tooth_width = 12.0           # tangential width of each tooth

gear_height = 25.0           # height of the toothed gear portion
hex_across_flats = 50.3      # hex boss across flats
hex_radius = hex_across_flats / math.sqrt(3.0)
hex_height = 31.7            # height of the hex boss above the gear

chamfer_size = 2.6           # chamfer on the outer cylindrical rim edges

# ---- Base cylinder ----
solid_body = Cylinder(outer_radius, gear_height)

# ---- Add external teeth (radial rectangular lugs around the rim) ----
for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = (
        Rot(0, 0, angle)
        * Pos(outer_radius - tooth_depth / 2.0, 0, 0)
        * Box(tooth_depth, tooth_width, gear_height)
    )
    solid_body = solid_body + tooth

# ---- Hexagonal boss on top of the gear ----
with BuildPart() as boss:
    with BuildSketch(Plane.XY.offset(gear_height / 2.0)) as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_height)
solid_body = solid_body + boss.part

# ---- Chamfer the two outer cylindrical rim edges ----
rim_edges = solid_body.edges().filter_by(GeomType.CIRCLE).filter_by(
    lambda e: abs(e.radius - outer_radius) < 1e-6
)
solid_body = chamfer(rim_edges, chamfer_size)

part = solid_body
part.name = "gear_with_hex_boss"
export_step(part, "output.step")