include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <lazy.scad>
use <rounded_collar.scad>

$fn = 67;

// Render/view settings
laser_cut = false;

cutaway_view = false;
cutaway_offset = 5;
show_card = false;
show_card_contacts = false;

// Printer settings
difference_fudge = 0.01;
extrusion_fudge = 0.1;
print_layer_height = 0.15;

// Default minimum thickness of any wall
wall_thickness = 2;

// Thickness of the engineering board support plate.
support_board_thickness = (3/16) * 25.4;

// Thickness of the card acrylic
acrylic_thickness = 3.25;

// Card dimensions
card_width = 54;
card_height = 81;
card_thickness = acrylic_thickness; // Allow thickness to be variable in case we add any 'decorations' around the card
card_corner_fillet = 2;

// The card holder has an open slot in front so the user can see the card.  The slot has a 'flange' on either side so
// that the card doesn't fall out.  This is the width of each of those flanges.
card_support_flange_width = 2;

// The card slot should be just a bit wider than the cards so that the user can slide it in and out of the slot easily
// and quickly.  The card_support_play indicates how much wider than the card the slot should be.
card_support_play = 2;

// This is the front-to-back play at the bottom of the card slot wedge.
card_wedge_play = 1;

card_wedge_width = card_width + card_support_play;

// This is the depth of the bottom of the card slot wedge.  It determines how much front-to-back play there will be when
// the card sits in the slot.
card_wedge_bottom_depth = card_thickness + card_wedge_play;

// This is the depth of the top of the card slot wedge.  It determines how 'steep' the slot wedge should be
// - how far forward will the card lean when sitting in the slot.  If the top depth is the same as the bottom depths,
//   the slot will be perfectly straight.
card_wedge_top_depth = card_wedge_bottom_depth + card_thickness;

front_wall_thickness = 3;
side_wall_thickness = 6;

// Dimensions of the card holder itself
holder_depth = card_wedge_top_depth + front_wall_thickness;
holder_width = card_width + side_wall_thickness * 2;

// Making the entire height of the holder the same as the card height will cause the card to poke out of the top of the
// holder by the same amount as the card_resting_height. Adjust the holder height up or down to change the 'poke out'.
holder_height = card_height;  
holder_corner_fillet = 3;

// At the bottom of the card we'll have the metal tabs that close the identification circuit.  The card holder will have
// matching contacts to sense the presence of these tabs.
card_contact_count = 5;
total_contact_count = 6; // Include one contact for the ground wire that the contacts close the circuit with

// How wide (left to right) is each contact plate
card_contact_width = 5;

// How thick (top to bottom) is each contact plate
card_contact_thickness = 3.175;

// How far should the card contact protrude under the card slot flange
card_contact_underlap = holder_depth - card_wedge_bottom_depth - front_wall_thickness;

// How far shuold the card contact plate stick out of the back of the engineering board.
card_contact_back_projection = 10;

// How long (front to back) is each contact plate
card_contact_depth = card_wedge_bottom_depth + card_contact_underlap + support_board_thickness + card_contact_back_projection;

// This is the bottom-most plate that supports the contact assembly
card_contact_support_thickness = 3;

// This is the y-position of the bottom of the card, resting on top of the contacts.
card_resting_height = card_contact_support_thickness + card_contact_thickness;

// Calculae how much space should there be between each contact

// Don't include the fillet corners in the width, we only want the card contacts on the flat part of the base of the
// card add an extra bit of fudge so that it's not too hard to apply the contacts to the card
card_contact_width_fudge = 4;
contact_available_width = card_width - (card_corner_fillet * 2) - card_contact_width_fudge;
contact_space_remaining = contact_available_width - (total_contact_count * card_contact_width);
contact_spacing = contact_space_remaining  / (total_contact_count - 1);

echo("In this model:");
echo(str("    there are ", total_contact_count, " card contacts"));
echo(str("    the card contacts are ", card_contact_width, " mm wide"));
echo(str("    the card contacts are spaced ", contact_spacing, " mm apart"));

LED_strip_width = 12;
LED_strip_length = card_width;
LED_strip_height = 1;
LED_width = 5.2;
LED_height = 2;
LED_wire_allotment = 5;
LED_offset_y = -LED_strip_width / 2;
strip_box_height = LED_strip_height + LED_height + acrylic_thickness;

mounting_pin_diam = 3;
mounting_pin_projection = 5;
mounting_pin_depth = support_board_thickness + mounting_pin_projection;

if(laser_cut) {
    projection(cut = true)
    tz(holder_depth / 2 - holder_corner_fillet - difference_fudge)
    rx(90)
    difference()
    {
        card_holder();
        ty(-holder_depth)
        {
            card_contacts();
            mounting_pins();
        }
    }
}
else {
    if(cutaway_view) {
        left_half(x = cutaway_offset, s = max(card_width, card_height) * 3)
        {
            card_holder();
            if(show_card) {
                card();
            }
            if(show_card_contacts) {
                card_contacts();    
            }
        }
    } else {
        card_holder();
        if(show_card) {
            card();
        }
        if(show_card_contacts) {
            card_contacts();    
        }
    }
}

module card_holder()
{
    difference()
    {
        card_blank();
        tz(difference_fudge) card_contacts();
        card_slot();
        card_wedge();
    }
    mounting_pins();
}

module card_blank()
{
    cuboid(
        [
            holder_width,
            holder_depth,
            holder_height
        ], 
        fillet=holder_corner_fillet,
        edges=EDGES_Y_ALL + EDGES_FRONT
    );
}

module mounting_pins()
{
    holder_sides_width = holder_width - card_wedge_width;

    ty(mounting_pin_depth / 2 + holder_depth / 2 - difference_fudge)
    xspread(holder_width - holder_sides_width / 2)
    zspread(holder_height * 0.75)
    ycyl(d=mounting_pin_diam, h = mounting_pin_depth);
}

module card_contacts()
{
    color("silver")
    tyz(
        card_contact_depth / 2 // Align from the front of the contact
            + holder_depth / 2 // line up with the back of the holder
            - card_wedge_bottom_depth // push into the holder the depth of the card wedge bottom
            - card_contact_underlap // push further into the holder under the card slot so that the card contacts don't see-saw out of their slots
        ,
        -holder_height / 2 + card_resting_height - card_contact_thickness / 2
    )
    xspread(card_contact_width + contact_spacing, n=total_contact_count)
    cuboid(
        [
            card_contact_width,
            card_contact_depth,
            card_contact_thickness
        ]
    );
}

module card_slot()
{
    // This is the cutout to make the card visible, it is inset from the card edges and the card_resting_height by
    // card_support_flange_width so the card won't fall out
    tz(card_support_flange_width + card_resting_height)
    cuboid([
        card_width - card_support_flange_width * 2, 
        holder_depth * 2, 
        card_height
    ]);
}

module card_wedge()
{
    card_cutout_height = (card_height - card_resting_height) + difference_fudge;

    // Card slot cutout - wedge
    tyz(holder_depth / 2 - card_wedge_bottom_depth / 2 + difference_fudge, 
        card_resting_height - holder_height / 2)
    prismoid(
        size1=[
            card_wedge_width,
            card_wedge_bottom_depth
        ], 
        size2=[
            card_wedge_width,
            card_wedge_top_depth
        ], 
        h=card_cutout_height, 
        shift=[0,  -(card_wedge_top_depth - card_wedge_bottom_depth) / 2]
    );
}

module card()
{
    color("red", 0.25)
    tyz(holder_depth / 2 - card_thickness / 2, card_resting_height)
    cuboid([card_width, card_thickness, card_height],
        fillet=card_corner_fillet,edges=EDGES_Y_ALL
    );
}

module led_strip()
{
    translate([0, LED_offset_y, 0])
    {
        color("black")
        upcube([LED_strip_length, LED_strip_width, LED_strip_height]);
        
        color("white")
        translate([0, 0, LED_strip_height])
        upcube([LED_strip_length, led_width, led_height]);

        translate([0, 0, LED_strip_height + led_height])
        color("#aaaaaa", 0.3)
        upcube([LED_strip_length, LED_strip_width, acrylic_thickness]);
    }
}