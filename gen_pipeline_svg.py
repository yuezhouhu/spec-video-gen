"""Build the editable TikZ pipeline: python3 gen_pipeline_svg.py.

Requires pdflatex, latex, dvisvgm, and Poppler (pdftoppm). Outputs a vector PDF,
vector SVG, and 400-dpi PNG. Temporary build files stay outside the repo.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"


def run(*args):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed:\n{result.stdout[-6000:]}\n{result.stderr[-3000:]}")


def main():
    required = ("pdflatex", "latex", "dvisvgm", "pdftoppm")
    missing = [program for program in required if not shutil.which(program)]
    if missing:
        raise SystemExit("Missing figure tools: " + ", ".join(missing))
    with tempfile.TemporaryDirectory(prefix="sdvg-pipeline-") as temporary:
        work = Path(temporary)
        run("pdflatex", "-interaction=nonstopmode", "-halt-on-error",
            f"-output-directory={work}", str(FIGURES / "pipeline.tex"))
        run("latex", "-interaction=nonstopmode", "-halt-on-error",
            f"-output-directory={work}", "-jobname=pipeline-svg",
            r"\def\SvgBuild{1}\input{" + str(FIGURES / "pipeline.tex") + "}")
        run("dvisvgm", "--no-fonts", "--exact", "--bbox=papersize",
            f"--output={work / 'pipeline.svg'}", str(work / "pipeline-svg.dvi"))
        run("pdftoppm", "-singlefile", "-r", "400", "-png",
            str(work / "pipeline.pdf"), str(work / "pipeline"))
        for extension in ("pdf", "svg", "png"):
            destination = FIGURES / f"pipeline.{extension}"
            shutil.copyfile(work / destination.name, destination)
            print(f"Saved {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
