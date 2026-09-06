import fitz

doc = fitz.open("uploads/imageMAE.pdf")

page = doc[2]  # page 3

for block in page.get_text("blocks"):
    x0, y0, x1, y1, text, *_ = block

    print(
        f"x0={x0:.1f}, "
        f"y0={y0:.1f}, "
        f"x1={x1:.1f}, "
        f"y1={y1:.1f}"
    )

    print(repr(text[:100]))
    print("-" * 60)