from PIL import Image, ImageChops

def compare_images(img1, img2, diff_out):
    image1 = Image.open(img1).convert("RGB")
    image2 = Image.open(img2).convert("RGB")

    diff = ImageChops.difference(image1, image2)
    diff.save(diff_out)

    diff_pixels = sum(diff.convert("L").point(lambda x: x > 0 and 1).getdata())
    total_pixels = image1.size[0] * image1.size[1]
    percent = (diff_pixels / total_pixels) * 100

    if percent == 0:
        status = "IDENTICAL"
    elif percent < 1:
        status = "MINOR"
    else:
        status = "CHANGED"

    return percent, status
