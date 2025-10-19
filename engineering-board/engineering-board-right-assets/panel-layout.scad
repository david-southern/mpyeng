include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <useful_constants.scad>

/* [Hidden] */
$fn = 89;   // Number of facets for circles
PIECES_PANEL = 1;
PIECES_CARD_TRAY = 2;
PIECES_LED_MOCK = 128;
PIECES_ALL = 255;

/* [Rendering Options] */ 
RenderPieces = 2; // [1: Panel, 2: Card Tray, 128: LED Mock, 255: All]

/* [Card Tray Options] */
card_tray_brim = 5;
card_tray_base_thickness = 3;
card_tray_outer_rounding = 9;
card_tray_inner_rounding = 4;
optix_thickness = 3.175;

/* [Hidden] */
eng_panel_width = 609;
eng_panel_height = 914;
eng_panel_thickness = 5;

pixel_size = 5;
pixel_thickness = 2;

led_grid_size = 80;
led_grid_thickness = pixel_thickness;

card_tray_thickness = card_tray_base_thickness + pixel_thickness + optix_thickness;

solder_pads_width = 30;
solder_pads_height = 60;
solder_pads_offset_right = 10;

function CheckRenderPieces(bit) = (RenderPieces & bit) == bit;

if (CheckRenderPieces(PIECES_PANEL))
{
    render()
    panel_base();
}

if (CheckRenderPieces(PIECES_CARD_TRAY))
{
    render()
    {
        card_tray(anchor=BOTTOM);
        up(card_tray_base_thickness)
        led_mock(anchor=BOTTOM);
    }
}

if (CheckRenderPieces(PIECES_LED_MOCK))
{
    render()
    led_mock(anchor=BOTTOM);
}

module card_tray(anchor=CENTER, spin=0, orient=UP)
{
    card_tray_size = led_grid_size + card_tray_brim * 2;
    attachable(anchor, spin, orient, size=[card_tray_size, card_tray_size, card_tray_thickness]) {
        color("white")
        diff(remove="inner_cutout solder_cutout")
        cuboid(
            [
                card_tray_size,
                card_tray_size,
                card_tray_thickness
            ],
            rounding = card_tray_outer_rounding,
            edges = "Z",
            anchor = CENTER
        )
        {
            position(BOTTOM)
            tag("inner_cutout")
            {
                up(card_tray_base_thickness + pixel_thickness)
                cuboid(
                    [
                        led_grid_size,
                        led_grid_size,
                        optix_thickness
                    ],
                    rounding = card_tray_inner_rounding,
                    edges = "Z",
                    anchor = BOTTOM

                );

                up(card_tray_base_thickness)
                cuboid(
                    [
                        led_grid_size,
                        led_grid_size,
                        pixel_thickness
                    ],
                    anchor = BOTTOM

                );
            }

            position(BOTTOM + RIGHT)
            tag("solder_cutout")
            {
                left(solder_pads_offset_right + card_tray_brim)
                cuboid(
                    [
                        solder_pads_width,
                        solder_pads_height,
                        card_tray_base_thickness * 2
                    ],
                    anchor = BOTTOM + RIGHT
                );
            }
        }
        children();
    }
}


module panel_base(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[eng_panel_width, eng_panel_height, eng_panel_thickness]) {
        color("white")
        cuboid(
            [
                eng_panel_width,
                eng_panel_height,
                eng_panel_thickness
            ],
            anchor = CENTER

        );
        children();
    }
}

module led_mock(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[led_grid_size, led_grid_size, led_grid_thickness]) {
        union()
        {
            recolor("white")
            xcopies(l = led_grid_size - 10, n = 8)
            ycopies(l = led_grid_size - 10, n = 8)
            {
                cuboid(
                    [
                        pixel_size,
                        pixel_size,
                        pixel_thickness
                    ],
                    anchor = CENTER
                );
            }
            {
                position(BOTTOM)
                {
                    recolor("#555555")
                    down(epsilon)
                    cuboid(
                        [
                            led_grid_size,
                            led_grid_size,
                            0.1
                        ],
                        anchor = BOTTOM
                    )
                    position(BOTTOM + RIGHT)
                    recolor("cyan")
                    left(solder_pads_offset_right)
                    cuboid(
                        [
                            solder_pads_width,
                            solder_pads_height,
                            1
                        ],
                        anchor = TOP + RIGHT
                    );
                }

                position(TOP)
                {
                    up(epsilon)
                    % cuboid(
                        [
                            led_grid_size,
                            led_grid_size,
                            optix_thickness
                        ],
                        rounding = card_tray_inner_rounding,
                        edges = "Z",
                        anchor = BOTTOM
                    );
                }
            }
        }
        children();
    }
}
