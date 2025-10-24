include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <../useful_stuff.scad>
include <../audio-jack-collar.scad>
include <../seven-seg-collar.scad>

/* [Hidden] */
PIECES_PANEL = 1;
PIECES_CARD_TRAY = 2;
PIECES_CARD_LAYOUT = 4;
PIECES_LED_MOCK = 128;
PIECES_ALL = 255;

/* [Rendering Options] */ 
RenderPieces = 4; // [1: Panel, 2: Card Tray, 4: Card Layout, 128: LED Mock, 5: Some, 255: All]
lo_rez_mocks = true;

/* [Power Bus Options] */
eng_panel_margin_x = 15;
eng_panel_margin_y = 15;
number_of_buses = 6;
cards_per_bus = 5;

/* [Switchboard Options] */
switchboard_elements_spacing = 3;

/* [Card Tray Options] */
card_tray_brim = 5;
card_tray_base_thickness = 3;
card_tray_outer_rounding = 9;
card_tray_inner_rounding = 4;
optix_thickness = 3.175;
show_led_grid = false;

/* [Hidden] */
eng_panel_width = 609;
eng_panel_height = 914;
eng_panel_thickness = 5;

switchboard_module_width = max(seven_seg_collar_base_width, audio_jack_collar_diameter);
switchboard_module_height = seven_seg_collar_base_height * 2 + audio_jack_collar_diameter + switchboard_elements_spacing * 2;
switchboard_module_depth = max(seven_seg_collar_depth, audio_jack_collar_depth);

pixel_size = 5;
pixel_thickness = 2;

led_grid_size = 80;
led_grid_thickness = pixel_thickness;

card_tray_size = led_grid_size + card_tray_brim * 2;
card_tray_thickness = card_tray_base_thickness + pixel_thickness + optix_thickness;


power_card_width = card_tray_size;
power_card_height = card_tray_size;

bus_total_height = eng_panel_height - eng_panel_margin_y * 2 - max(switchboard_module_height, power_card_height);
bus_spacing_y = bus_total_height / (number_of_buses - 1);

bus_card_width = eng_panel_width - eng_panel_margin_x * 3 - power_card_width - switchboard_module_width;
bus_card_spacing_x = bus_card_width / (cards_per_bus - 1);

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
        if (show_led_grid)
        {
            up(card_tray_base_thickness)
            led_mock(anchor=BOTTOM);
        }
    }
}

if (CheckRenderPieces(PIECES_CARD_LAYOUT))
{
    render()
    {

        panel_base()
        {
            position(LEFT)
            right(eng_panel_margin_x)
            ycopies(bus_spacing_y, n = number_of_buses)
            switchboard_module(anchor=LEFT);

            position(RIGHT)
            left(eng_panel_margin_x + power_card_width / 2)
            ycopies(bus_spacing_y, n = number_of_buses)
            xcopies(-bus_card_spacing_x, n = cards_per_bus, sp = [0, 0, 0])
            card_tray(anchor=BOTTOM);
        }
    }
}

if (CheckRenderPieces(PIECES_LED_MOCK))
{
    render()
    led_mock(anchor=BOTTOM);
}


module switchboard_module(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[switchboard_module_width, switchboard_module_height, switchboard_module_depth])
    {
        color("steelblue")
        if(lo_rez_mocks) {
            cyl(d = audio_jack_collar_diameter, h = audio_jack_collar_depth,  anchor = BOTTOM)
            {
                position(BACK)
                back(switchboard_elements_spacing)
                cuboid(
                    [
                        seven_seg_collar_base_width,
                        seven_seg_collar_base_height,
                        seven_seg_collar_depth
                    ],
                    rounding = 15,
                    edges = "Z",
                    anchor = BOTTOM + FRONT
                );            

                position(FRONT)
                fwd(switchboard_elements_spacing)
                cuboid(
                    [
                        seven_seg_collar_base_width,
                        seven_seg_collar_base_height,
                        seven_seg_collar_depth
                    ],
                    rounding = 15,
                    edges = "Z",
                    anchor = BOTTOM + BACK
                );            
            };

        } else {
            audio_jack_collar(anchor = BOTTOM)
            {
                position(BACK)
                back(switchboard_elements_spacing)
                seven_seg_collar(anchor = BOTTOM + FRONT);

                position(FRONT)
                fwd(switchboard_elements_spacing)
                seven_seg_collar(anchor = BOTTOM + BACK);
            };
        }

        children();
    }
}

module card_tray(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[card_tray_size, card_tray_size, card_tray_thickness]) {
        color("mediumseagreen")
        if(lo_rez_mocks) {
            cuboid(
                [
                    card_tray_size,
                    card_tray_size,
                    card_tray_thickness
                ],
                rounding = card_tray_outer_rounding,
                edges = "Z",
                anchor = CENTER
            );
        } else 
        {
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
