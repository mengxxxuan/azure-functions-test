# inspect_pdf_pages.py
import fitz  # PyMuPDF
import os

def inspect_pdf(pdf_path: str, pixel_limit: int = 50_000_000, dpi_list=(200, 300, 400)):
    """
    逐页检查 PDF：
      - 页尺寸（pt / inch / mm）
      - 按给定 DPI 预估栅格化后像素
      - 该页最大嵌入图片的实际像素（width*height）
    pixel_limit: 用于提示是否超过阈值（默认 50MP）
    """
    doc = fitz.open(pdf_path)
    print(f"📄 File: {pdf_path}  | Pages: {doc.page_count}\n")

    for i in range(doc.page_count):
        page = doc[i]
        rect = page.rect  # 单位：points(1pt=1/72 inch)
        w_pt, h_pt = rect.width, rect.height
        w_in, h_in = w_pt / 72.0, h_pt / 72.0
        w_mm, h_mm = w_in * 25.4, h_in * 25.4

        print(f"—— Page {i+1} ——")
        print(f"Page size: {w_pt:.1f}×{h_pt:.1f} pt  |  {w_in:.2f}×{h_in:.2f} in  |  {w_mm:.1f}×{h_mm:.1f} mm")

        # 按不同 DPI 粗略估计页栅格化后的像素（仅供参考）
        for dpi in dpi_list:
            px_w = int(round(w_in * dpi))
            px_h = int(round(h_in * dpi))
            mp = px_w * px_h / 1e6
            warn = "  ⚠️ >50MP" if (px_w * px_h) > pixel_limit else ""
            print(f"  @ {dpi} DPI ≈ {px_w}×{px_h} px  ({mp:.1f} MP){warn}")

        # 提取该页嵌入图片，找出最大的像素尺寸
        images = page.get_images(full=True)
        if not images:
            print("Embedded images: 0\n")
            continue

        max_pixels = 0
        max_wh = (0, 0)
        for img in images:
            xref = img[0]
            try:
                info = doc.extract_image(xref)
                w, h = info.get("width"), info.get("height")
                if w and h:
                    pixels = w * h
                    if pixels > max_pixels:
                        max_pixels = pixels
                        max_wh = (w, h)
            except Exception:
                # 某些对象可能不是常规图片流，忽略即可
                pass

        if max_pixels > 0:
            mp = max_pixels / 1e6
            warn = "  ⚠️ >50MP" if max_pixels > pixel_limit else ""
            print(f"Embedded images: {len(images)} | largest: {max_wh[0]}×{max_wh[1]} px  ({mp:.1f} MP){warn}\n")
        else:
            print(f"Embedded images: {len(images)} (no dimension info)\n")

    doc.close()

if __name__ == "__main__":
    # 替换为你的 PDF 路径
    pdf_path = "travelguide_epos_platinum_SompoJapan.pdf"
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)
    inspect_pdf(pdf_path)