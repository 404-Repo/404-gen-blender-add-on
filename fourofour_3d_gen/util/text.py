import blf
import bpy


def wrap(text: str, width: int) -> list[str]:
    """
    Wrap the given text to the given width.

    Args:
        width: The maximum pixel width of each row.
        text: The text to be split and returned.

    Returns:
        A list of the split up text and empty space if necessary.
    """
    return_text = []
    row_text = ""

    system = bpy.context.preferences.system
    dpi = 72 if system.ui_scale >= 1 else system.dpi
    blf.size(0, dpi)

    for word in text.split():
        word = f" {word}"
        line_len, _ = blf.dimensions(0, row_text + word)

        if line_len <= (width - 16):
            row_text += word
        else:
            return_text.append(row_text)
            row_text = word

    if row_text:
        return_text.append(row_text)

    return return_text
