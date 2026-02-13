from pathlib import Path
import fitz

def stepper(input_pdf_path, target_page=0, start_line=0, end_line=None, step=1000, bins=None, output_root=None):
    """
    Generates incremental PDF snapshots by truncating the content stream line by line.
    
    This method is used to identify the exact location of specific drawing operators 
    (like 'Do') that may be obscuring background content. It creates a series of 
    PDF files, each including an increasing amount of the original stream data.

    Args:
        target_page (int): 0-based page index.
        start_line (int): Line number to start stepping.
        end_line (int, optional): Last line to analyze. Defaults to total lines.
        step (int): Number of lines per step. (Ignored if bins is set)
        bins (int, optional): If set, divides the range into N equal steps.
        output_root (str, optional): Default is '{input_stem}_steps'.
    """

    p = Path(input_pdf_path)
    if not p.exists():
        print(f"Error: {input_pdf_path} not found.")
        return
    
    doc = fitz.open(str(p))

    # Page Validation
    if not (0 <= target_page < len(doc)):
        print(f"Error: target_page {target_page} is out of range (0-{len(doc)-1}).")
        doc.close()
        return
    
    page = doc[target_page]
    contents_xrefs = page.get_contents()
    full_raw_data = b"\n".join([doc.xref_stream(x) for x in contents_xrefs])
    lines = full_raw_data.split(b"\n")
    total_lines = len(lines)
    
    # Range and Step/Bins Validation
    end_line = min(end_line or total_lines, total_lines)
    if bins is not None:
        if bins <= 0:
            print(f"Error: bins must be positive.")
            doc.close()
            return
        step = max(1, (end_line - start_line) // bins)
        target_range = [
                start_line + (end_line - start_line) * i // bins 
                for i in range(bins + 1)
            ]
    else:
        target_range = [i for i in range(start_line, end_line + step, step) if i <= end_line]
        if target_range[-1] < end_line:
            target_range.append(end_line)
        
    # File count confirmation
    num_files = len(target_range)
    if num_files > 100:
        if input(f"Warning: Generate {num_files} PDFs? (y/n): ").lower() != 'y':
            doc.close()
            return

    out_dir = Path(output_root or p.parent / f"{p.stem}_steps")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyze Info: {start_line} - {end_line} ({'bins' if bins else 'step'}: {bins if bins else step})")

    for idx, i in enumerate(target_range):
        current_data = b"\n".join(lines[:i]) + b"\nQ" * 10
        
        new_doc = fitz.open(str(p))
        for xref in contents_xrefs:
            new_doc.update_stream(xref, b" ") 
        new_doc.update_stream(contents_xrefs[0], current_data)
        
        save_path = out_dir / f"page_{target_page}_step_{i:06d}.pdf"
        new_doc.save(str(save_path))
        new_doc.close()
        
        if (idx + 1) % 20 == 0:
            print(f"Progress: {idx + 1}/{num_files} files generated...")

    doc.close()
    print(f"Success: PDF steps generated in '{out_dir}'")
