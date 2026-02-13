from pathlib import Path
import fitz

def extractor(input_pdf_path, output_root=None, join=False):
    """
    Extracts content streams from a PDF file.

    Args:
        input_pdf_path (str): Path to the source PDF.
        output_root (Path/str, optional): Destination directory. Defaults to input_filename_streams/.
        join (bool): If True, concatenates all streams per page into a single file.
    """
    
    p = Path(input_pdf_path)
    if not p.exists():
        print(f"Error: {input_pdf_path} not found.")
        return

    if output_root is None:
        output_root = p.parent / f"{p.stem}_streams"
    else:
        output_root = Path(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(p))

    for i, page in enumerate(doc):
            contents = page.get_contents()
            
            if join:
                full_stream = b"".join([doc.xref_stream(xref) for xref in contents])
                filename = f"page{i+1:03d}_full.txt"
                save_path = output_root / filename
                with open(save_path, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(full_stream.decode("latin-1", errors="ignore"))
            else:
                for j, content_xref in enumerate(contents):
                    stream = doc.xref_stream(content_xref)
                    filename = f"page{i+1:03d}_s{j:02d}_xref{content_xref}.txt"
                    with open(output_root / filename, "w", encoding="utf-8", errors="ignore") as f:
                        f.write(stream.decode("latin-1", errors="ignore"))
                
    print(f"Success: Extracted streams to {output_root}")
    doc.close()