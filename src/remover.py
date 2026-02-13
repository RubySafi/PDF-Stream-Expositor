import fitz
from pathlib import Path

def do_remover(input_pdf_path, target_page=0, start_line=0, end_line=None, target_lines=None, output_path=None):
    """
    Generate a modified PDF by commenting out 'Do' operators within a specified range.

    This method allows for pinpoint suppression of XObjects (images, forms, etc.) 
    that may be obscuring background content, such as hidden formulas.

    Args:
        target_page (int): 0-based page index.
        start_line (int): Start line for range-based removal.
        end_line (int, optional): End line for range-based removal.
        target_lines (list, optional): Specific line numbers to comment out.
        output_path (str, optional): Default is '{stem}_rem.pdf'.
    """
    p = Path(input_pdf_path)
    out_path = Path(output_path or p.parent / f"{p.stem}_rem.pdf")
    
    doc = fitz.open(str(p))

    # Page Validation
    if not (0 <= target_page < len(doc)):
        print(f"Error: target_page {target_page} is out of range (0-{len(doc)-1}).")
        doc.close()
        return
    
    # target_lines Validation
    if isinstance(target_lines, int):
        target_lines = [target_lines]

    page = doc[target_page]
    contents_xrefs = page.get_contents()
    
    full_raw_data = b"\n".join([doc.xref_stream(x) for x in contents_xrefs])
    lines = full_raw_data.split(b"\n")
    
    end_line = end_line or len(lines)
    
    new_lines = []
    comment_count = 0
    
    for idx, line in enumerate(lines):
        decoded_line = line.decode("latin-1")
        should_comment = False
        
        if target_lines and idx in target_lines:
            should_comment = True
        
        elif start_line <= idx <= end_line:
            if " Do" in decoded_line:
                should_comment = True
                
        if should_comment:
            new_lines.append(b"% " + line)
            comment_count += 1
        else:
            new_lines.append(line)

    new_data = b"\n".join(new_lines)
    for i, xref in enumerate(contents_xrefs):
        doc.update_stream(xref, new_data if i == 0 else b" ")
    
    doc.save(str(out_path))
    doc.close()
    if comment_count == 0:
        print(f"Warning: No 'Do' operators found in the specified range.")
    else:
        print(f"Success: {out_path} (Range: {start_line}-{end_line}, Modified: {comment_count} lines)")