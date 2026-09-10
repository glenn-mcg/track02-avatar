from pathlib import Path
from PIL import Image


def test_generated_image_can_be_evaluated():
    """
    Verify that the generated avatar is a readable image
    with the expected resolution.
    """

    image_file = (
        Path("outputs")
        / "job_004"
        / "avatar-output"
        / "job_004_1.png"
    )

    assert image_file.exists()

    with Image.open(image_file) as image:
        assert image.width == 1024
        assert image.height == 1024

        # Force PIL to actually decode the image.
        image.load()


def test_generated_image_has_nonzero_file_size():
    """
    Verify that the evaluated output is not empty.
    """

    image_file = (
        Path("outputs")
        / "job_004"
        / "avatar-output"
        / "job_004_1.png"
    )

    assert image_file.exists()
    assert image_file.stat().st_size > 0