from luminous_photos import views


class FakeImage:
    def __init__(self, w, h):
        self.width = w
        self.height = h


def test_dimension_scaling_1():
    img = FakeImage(1000, 750)
    size = views.proportionally_scale_dimensions(img, (600, 800))
    assert size == (600, 450)


def test_dimension_scaling_2():
    img = FakeImage(1000, 750)
    size = views.proportionally_scale_dimensions(img, (1280, 720))
    assert size == (960, 720)
