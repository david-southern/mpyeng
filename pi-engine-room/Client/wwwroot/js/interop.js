let animationHandle;
let image;

async function onePingOnly() {
    if (!image) {
        image = document.getElementById("coreImage");
    }

    const response = await fetch('/animation-frame', { cache: "no-cache" });
    const imageText = await response.text();
    image.src = imageText;
}

export async function startAnimation(frameRate) {
    animationHandle = setInterval(onePingOnly, (1000 / frameRate) || 100);
}

export function stopAnimation() {
    if (animationHandle) {
        clearInterval(animationHandle);
        animationHandle = undefined;
    }
}

setTimeout(onePingOnly, 1000);