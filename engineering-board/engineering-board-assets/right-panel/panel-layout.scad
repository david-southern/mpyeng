include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <../useful-stuff.scad>
include <../audio-jack-collar.scad>
include <../seven-seg-collar.scad>
include <card-tray-full.scad>

/* [Hidden] */

/* [Rendering Options] */
RenderPieces = 4; // [1: Panel, 4: Card Layout, 255: All]
lo_rez_mocks = true;

/* [Power Bus Options] */
eng_panel_margin_x = 15;
eng_panel_margin_y = 15;
number_of_buses = 6;
cards_per_bus = 4;

/* [Switchboard Options] */
switchboard_elements_spacing = 3;

/* [Hidden] */
switchboard_module_width = max(seven_seg_collar_base_width, audio_jack_collar_diameter);
switchboard_module_height = seven_seg_collar_base_height * 2 + audio_jack_collar_diameter + switchboard_elements_spacing * 2;
switchboard_module_depth = max(seven_seg_collar_depth, audio_jack_collar_depth);

echo(
    str(
        "Seven Seg Dimension: ", [
            seven_seg_collar_base_width,
            " x ",
            seven_seg_collar_base_height,
            " x ",
            seven_seg_collar_depth,
        ]
    )
);

echo(
    str(
        "Audio Jack Dimension: ", [
            audio_jack_collar_diameter,
            " x ",
            audio_jack_collar_diameter,
            " x ",
            audio_jack_collar_depth,
        ]
    )
);

bus_total_height = eng_panel_height - eng_panel_margin_y * 2 - max(switchboard_module_height, card_bay_height);
bus_spacing_y = bus_total_height / (number_of_buses - 1);

bus_card_width = eng_panel_width - eng_panel_margin_x * 3 - card_bay_width - switchboard_module_width;
bus_card_spacing_x = bus_card_width / (cards_per_bus - 1);

if (CheckRenderPieces(PIECES_PANEL)) {
    render()
        panel_base();
}

if (CheckRenderPieces(PIECES_CARD_LAYOUT)) {
    render() {

        panel_base() {
            position(LEFT)
                right(eng_panel_margin_x)
                    ycopies(bus_spacing_y, n=number_of_buses)
                        switchboard_module(anchor=LEFT);

            position(RIGHT)
                left(eng_panel_margin_x + card_bay_width / 2)
                    ycopies(bus_spacing_y, n=number_of_buses)
                        xcopies(-bus_card_spacing_x, n=cards_per_bus, sp=[0, 0, 0])
                            card_tray(anchor=BOTTOM);
        }
    }
}

module switchboard_module(anchor = CENTER, spin = 0, orient = UP) {
    attachable(anchor, spin, orient, size=[switchboard_module_width, switchboard_module_height, switchboard_module_depth]) {
        color("steelblue") if (lo_rez_mocks) {
            cyl(d=audio_jack_collar_diameter, h=audio_jack_collar_depth, anchor=BOTTOM) {
                position(BACK)
                    back(switchboard_elements_spacing)
                        cuboid(
                            [
                                seven_seg_collar_base_width,
                                seven_seg_collar_base_height,
                                seven_seg_collar_depth,
                            ],
                            rounding=15,
                            edges="Z",
                            anchor=BOTTOM + FRONT
                        );

                position(FRONT)
                    fwd(switchboard_elements_spacing)
                        cuboid(
                            [
                                seven_seg_collar_base_width,
                                seven_seg_collar_base_height,
                                seven_seg_collar_depth,
                            ],
                            rounding=15,
                            edges="Z",
                            anchor=BOTTOM + BACK
                        );
            }
            ;
        } else {
            audio_jack_collar(anchor=BOTTOM) {
                position(BACK)
                    back(switchboard_elements_spacing)
                        seven_seg_collar(anchor=BOTTOM + FRONT);

                position(FRONT)
                    fwd(switchboard_elements_spacing)
                        seven_seg_collar(anchor=BOTTOM + BACK);
            }
            ;
        }

        children();
    }
}

module panel_base(anchor = CENTER, spin = 0, orient = UP) {
    attachable(anchor, spin, orient, size=[eng_panel_width, eng_panel_height, eng_panel_thickness]) {
        color("white")
            cuboid(
                [
                    eng_panel_width,
                    eng_panel_height,
                    eng_panel_thickness,
                ],
                anchor=CENTER
            );
        children();
    }
}
