from ..image import Image


class ImagePreview(Image):
    '''Blender-editor variant of :class:`~uplogic.ui.image.Image`.

    Overrides the fragment shader to apply gamma correction (``pow(color, 1)``)
    so that textures sampled in the editor viewport match their on-disk colours.
    '''

    fragment_shader = """
    in vec2 uv;
    out vec4 fragColor;

    uniform sampler2D image;
    uniform float alpha = 1.0;

    void main() {
        vec4 color = mix(vec4(0.0), texture(image, uv), alpha);
        fragColor = pow(color, vec4(1));
    }
    """