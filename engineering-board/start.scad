include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <useful_constants.scad>

/* [Hidden] */
$fn = 89;   // Number of facets for circles
PIECES_BASE = 1;
PIECES_SUBMODULE = 2;
PIECES_ALL = 255;

/* [Rendering Options] */ 
RenderPieces = 255; // [1: Base Object, 2: Submodule, 255: All]

/* [Hidden] */
function CheckRenderPieces(bit) = (RenderPieces & bit) == bit;

if (CheckRenderPieces(PIECES_BASE))
{
    echo(str("Rendering base object"));

    render()
    thingy(23, 3);
}

module thingy(cylinder_diameter, cylinder_length, anchor=CENTER, spin=0, orient=UP)
{
    thingy_width = cylinder_diameter;
    thingy_depth = cylinder_diameter;
    thingy_height = cylinder_length;

    attachable(anchor, spin, orient, size=[thingy_width, thingy_depth, thingy_height]) {
        cylinder(d = cylinder_diameter, h = cylinder_length, center = true);
        children();
    }
}
