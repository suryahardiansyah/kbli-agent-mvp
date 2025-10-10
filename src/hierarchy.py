def build_hierarchy(kbli_list):
    """
    Build a cascading hierarchy of KBLI codes like SPK web app.
    """
    tree = {}
    for entry in kbli_list:
        code = entry["kbli"]
        if len(code) < 5:  # skip incomplete
            continue
        prefix = code[:-1]
        node = tree.setdefault(prefix, [])
        node.append(entry)
    return tree

def format_hierarchy(results):
    """Format hierarchical KBLI results for WA-style chat."""
    lines = []
    for r in results:
        kbli, title = r["kbli"], r["judul"]
        indent = " " * (len(kbli) - 1)
        lines.append(f"{indent}{kbli}  {title}")
    return "\n".join(lines)
