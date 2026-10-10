from build123d import *

# --- Dimensions from the drawing ---
hex_across_flats = 53.3          # hexagon across flats
hex_thickness    = 20.0          # hexagonal flange thickness
cyl_diameter     = 34.8          # cylindrical barrel diameter
cyl_length       = 60.0          # barrel length from flange face
total_length     = 80.0          # overall length (hex back face to barrel tip)
hex_circumradius = hex_across_flats / 3**0.5   # ~30.77

# --- Hexagonal flange (axis along X) ---
with BuildPart() as hex_p:
    with BuildSketch(Plane.YZ) as s:
        RegularPolygon(hex_circumradius, 6)
    extrude(amount=hex_thickness)
hex_solid = hex_p.part

# --- Cylindrical barrel, starting at the flange front face ---
cyl_solid = (
    Pos(hex_thickness + cyl_length / 2, 0, 0)
    * Rot(0, 90, 0)
    * Cylinder(cyl_diameter / 2, cyl_length)
)

part = hex_solid + cyl_solid
part.name = "hex_flange_barrel"
export_step(part, "output.step")