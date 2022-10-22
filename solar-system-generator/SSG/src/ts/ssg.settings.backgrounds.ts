import * as THREE from 'three';

import blackBackground from '../images/black.png';

import milkyWay1 from '../images/milky-way-1.jpg';
import milkyWay2 from '../images/milky-way-2.jpg';
import nebulaCarinaNorth from '../images/nebula-carina-north.jpg';
import nebulaCarinaPillar from '../images/nebula-carina-pillar.jpg';
import nebulaFlamingStar from '../images/nebula-flaming-star.jpg';
import nebulaHorseFlame from '../images/nebula-horse-flame.jpg';
import nebulaM42 from '../images/nebula-m42-gleason.jpg';
import nebulaMgc6751 from '../images/nebula-ngc6751.jpg';
import starsDeepField from '../images/stars-hubble-deep-field.jpg';
import starsM34 from '../images/stars-m34-franke.jpg';
import starsM46 from '../images/stars-m46-m47.jpg';
import starsM67 from '../images/stars-m67.jpg';

export const GRID_TYPE_RECTANGULAR = 'Rectangular';
export const GRID_TYPE_POLAR = 'Polar';
export const GRID_TYPE_NONE = 'None';

export class BackgroundImageData {
    constructor(public Description: string, public URL: any, public Brightness?: number, public Contrast?: number) {
    }
}

export const BackgroundImages: BackgroundImageData[] = [
    new BackgroundImageData("Black", blackBackground),
    new BackgroundImageData("Milky Way 1", milkyWay1),
    new BackgroundImageData("Milky Way 2", milkyWay2),
    new BackgroundImageData("Nebula 1 - Carina", nebulaCarinaPillar),
    new BackgroundImageData("Nebula 2 - Carina/Clombari", nebulaCarinaNorth),
    new BackgroundImageData("Nebula 3 - Horse & Flame", nebulaHorseFlame),
    new BackgroundImageData("Nebula 4 - Flaming Star", nebulaFlamingStar),
    new BackgroundImageData("Nebula 5 - M42", nebulaM42),
    new BackgroundImageData("Nebula 6", nebulaMgc6751),
    new BackgroundImageData("Stars 1 - M46/M47", starsM46),
    new BackgroundImageData("Stars 2 - Deep Field", starsDeepField),
    new BackgroundImageData("Stars 3 - M34", starsM34),
    new BackgroundImageData("Stars 4 - M67", starsM67),
];

export const DefaultBackgroundImage = BackgroundImages[0];

