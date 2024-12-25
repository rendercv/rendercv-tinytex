from rendercv_tinytex import run_pdftex


def test_run_pdftex(tmp_path):
    latex_file_path = tmp_path / "test.tex"

    latex_file_path.write_text(
        "\\documentclass{article}\n"
        "\\title{Test}\n"
        "\\begin{document}\n"
        "\\maketitle\n"
        "Hello, world!\n"
        "\\end{document}\n"
    )

    run_pdftex(latex_file_path)

    pdf_file_path = latex_file_path.with_suffix(".pdf")
    assert pdf_file_path.is_file()
