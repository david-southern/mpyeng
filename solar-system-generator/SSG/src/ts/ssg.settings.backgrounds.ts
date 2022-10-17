import * as THREE from 'three';

import milkyWay1 from '../images/milky-way-1.jpg';
import milkyWay2 from '../images/milky-way-2.jpg';
import nebulaCarniaNorth from '../images/nebula-carina-north.jpg';
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
    public Description?: string;
    public URL?: string;
    public Brightness?: number;
    public Contrast?: number;
    public Lighten?: number;
    public Darken?: number;
    public Blur?: number;

    constructor(name: string, image?: any, color?: string) {
        this.Description = name;
        this.URL = image ?? color;
    }
}

const mw2 = new BackgroundImageData("Milky Way 2", milkyWay2);
mw2.Brightness = -0.25;
mw2.Contrast = -0.65;

export const BackgroundImages: BackgroundImageData[] = [
    new BackgroundImageData("None - DkBlue", null, "#080820"),
    new BackgroundImageData("None - Black", null, "#000000"),
    new BackgroundImageData("None - DkGreen", null, "#081008"),
    new BackgroundImageData("Milky Way 1", milkyWay1),
    mw2,
    new BackgroundImageData("Nebula 1 - Carina", nebulaCarinaPillar),
    new BackgroundImageData("Nebula 2 - Carina/Clombari", nebulaCarniaNorth),
    new BackgroundImageData("Nebula 3 - Horse & Flame", nebulaHorseFlame),
    new BackgroundImageData("Nebula 4 - Flaming Star", nebulaFlamingStar),
    new BackgroundImageData("Nebula 5 - M42", nebulaM42),
    new BackgroundImageData("Nebula 6", nebulaMgc6751),
    new BackgroundImageData("Stars 1 - M46/M47", starsM46),
    new BackgroundImageData("Stars 2 - Deep Field", starsDeepField),
    new BackgroundImageData("Stars 3 - M34", starsM34),
    new BackgroundImageData("Stars 4 - M67", starsM67),
];

const makeIdentityLutTexture = function () {
    const identityLUT = new Uint8Array([
        0, 0, 0, 255,  // black
        255, 0, 0, 255,  // red
        0, 0, 255, 255,  // blue
        255, 0, 255, 255,  // magenta
        0, 255, 0, 255,  // green
        255, 255, 0, 255,  // yellow
        0, 255, 255, 255,  // cyan
        255, 255, 255, 255,  // white
    ]);

    return function (filter: THREE.TextureFilter) {
        const texture = new THREE.DataTexture(identityLUT, 4, 2, THREE.RGBAFormat);
        texture.minFilter = filter;
        texture.magFilter = filter;
        texture.needsUpdate = true;
        texture.flipY = false;
        return texture;
    };
}();


const lutTextures = [
    { name: 'identity', size: 2, texture: makeIdentityLutTexture(THREE.LinearFilter) },
    { name: 'identity not filtered', size: 2, texture: makeIdentityLutTexture(THREE.NearestFilter) },
];

const lutShader = {
    uniforms: {
        tDiffuse: { value: null },
        lutMap: { value: null },
        lutMapSize: { value: 1, },
    },
    vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
        }
      `,
    fragmentShader: `
        #include <common>
     
        #define FILTER_LUT true
     
        uniform sampler2D tDiffuse;
        uniform sampler2D lutMap;
        uniform float lutMapSize;
     
        varying vec2 vUv;
     
        vec4 sampleAs3DTexture(sampler2D tex, vec3 texCoord, float size) {
          float sliceSize = 1.0 / size;                  // space of 1 slice
          float slicePixelSize = sliceSize / size;       // space of 1 pixel
          float width = size - 1.0;
          float sliceInnerSize = slicePixelSize * width; // space of size pixels
          float zSlice0 = floor( texCoord.z * width);
          float zSlice1 = min( zSlice0 + 1.0, width);
          float xOffset = slicePixelSize * 0.5 + texCoord.x * sliceInnerSize;
          float yRange = (texCoord.y * width + 0.5) / size;
          float s0 = xOffset + (zSlice0 * sliceSize);
     
          #ifdef FILTER_LUT
     
            float s1 = xOffset + (zSlice1 * sliceSize);
            vec4 slice0Color = texture2D(tex, vec2(s0, yRange));
            vec4 slice1Color = texture2D(tex, vec2(s1, yRange));
            float zOffset = mod(texCoord.z * width, 1.0);
            return mix(slice0Color, slice1Color, zOffset);
     
          #else
     
            return texture2D(tex, vec2( s0, yRange));
     
          #endif
        }
     
        void main() {
          vec4 originalColor = texture2D(tDiffuse, vUv);
          gl_FragColor = sampleAs3DTexture(lutMap, originalColor.xyz, lutMapSize);
        }
      `,
};

const lutNearestShader = {
    uniforms: Object.assign({}, lutShader.uniforms),
    vertexShader: lutShader.vertexShader,
    fragmentShader: lutShader.fragmentShader.replace('#define FILTER_LUT', '//'),
};

// const effectLUT = new THREE.ShaderPass(lutShader);
// effectLUT.renderToScreen = true;
// const effectLUTNearest = new THREE.ShaderPass(lutNearestShader);
// effectLUTNearest.renderToScreen = true;

