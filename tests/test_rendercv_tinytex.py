from rendercv_tinytex import run_pdftex


def test_run_pdftex(tmp_path):
    latex_file_path = tmp_path / "test.tex"

    latex_file_path.write_text(
        "\\documentclass{article}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage{charter}\n"
        "\\begin{document}\n"
        "\\section{Hello, world!}\n"
        "This is a test.\n"
        "\\end{document}\n"
    )

    pdf_file_path = run_pdftex(latex_file_path)

    assert pdf_file_path.is_file()
