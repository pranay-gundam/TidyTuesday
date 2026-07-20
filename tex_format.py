from typing import List, Tuple
from pyfredapi import SeriesInfo
from datetime import datetime, timedelta

from latex_utils import escape_latex

def init_folder_tex(filepath: str, cur_date: str) -> None:
    filepath_week_sum = f"{filepath}/weekly_summary.tex"
    filepath_week_main = f"{filepath}/main_file.tex"

    filepath_template_begin1 = f"tex_templates/doc_begin_pt1.txt"
    filepath_template_begin2 = f"tex_templates/doc_begin_pt2.txt"
    filepath_template_begin3 = f"tex_templates/doc_begin_pt3.txt"
    filepath_template_packages = f"tex_templates/packages.txt"

    # Read the contents of the template begin file
    with open(filepath_template_begin1, "r") as template_file:
        template_begin1 = template_file.read()

    with open(filepath_template_begin2, "r") as template_file:
        template_begin2 = template_file.read()

    with open(filepath_template_begin3, "r") as template_file:
        template_begin3 = template_file.read()

    # Read the contents of the template packages file
    with open(filepath_template_packages, "r") as template_file:
        template_packages = template_file.read()

    # Write the template content to the weekly summary file
    with open(filepath_week_sum, "w") as f:
        f.write("\\section{Weekly Summary}\n")
    
    date_obj = datetime.strptime(cur_date, "%Y-%m-%d")

    # Write the template content to the main file
    with open(filepath_week_main, "w") as f:
        f.write(template_packages)
        f.write("\n\n")
        f.write(template_begin1)
        f.write("pdftitle = {TidyTuesday Week " + str(date_obj.isocalendar()[1]) + "},\n")
        f.write(template_begin2)
        f.write("\\title{\\textbf{TidyTuesday Week " + str(date_obj.isocalendar()[1]) + "}}\n")
        f.write(template_begin3)
        f.write("\n")
        f.write("\\include{tex_things/day_" + date_obj.strftime("%Y-%m-%d") + "}\n")
        f.write("\\include{tex_things/day_" + (date_obj + timedelta(days=1)).strftime("%Y-%m-%d") + "}\n")
        f.write("\\include{tex_things/day_" + (date_obj + timedelta(days=2)).strftime("%Y-%m-%d") + "}\n")
        f.write("\\include{tex_things/day_" + (date_obj + timedelta(days=3)).strftime("%Y-%m-%d") + "}\n")
        f.write("\\include{tex_things/day_" + (date_obj + timedelta(days=4)).strftime("%Y-%m-%d") + "}\n")
        f.write("\\include{tex_things/day_" + (date_obj + timedelta(days=5)).strftime("%Y-%m-%d") + "}\n")
        f.write("\\include{tex_things/day_" + (date_obj + timedelta(days=6)).strftime("%Y-%m-%d") + "}\n")
        f.write("\n\\end{document}\n")

def daily_tex_update(file_path: str, cur_date: str, infos: List[SeriesInfo]) -> None:
    day_filepath = file_path + f"/tex_things/day_{cur_date}.tex"

    series_infos = []
    for serie in infos:
        series_infos.append(generate_series_info_latex(serie))

    with open(day_filepath, "w") as f:
        f.write("\section{Date: " + cur_date + "}\n")
        for table in series_infos:
            f.write(table)

        f.write("\\subsection{Raw Regression}\n")
        f.write("\\noindent Regresses the two series against each other directly. A significant "
                "result here can come just as easily from both series sharing a long-run trend as "
                "from any real relationship.\n\n")
        f.write("\\input{" + f"tex_tables/regression_table_{cur_date}.tex" + "}\n\n")
        f.write("\\begin{figure}\n")
        f.write("\\centering\n")
        f.write("\\includegraphics[scale = 0.9]{" + f"plots/plot_{cur_date}.png" + "}\n")
        f.write("\\caption{Raw Regression Plot for " + cur_date + "}\n")
        f.write("\\end{figure}\n")
        f.write("\\newpage\n")

        f.write("\\subsection{Detrended Regression}\n")
        f.write("\\noindent Regresses the residuals of each series after removing its own linear "
                "time trend, so a shared trend can no longer drive the result on its own. A "
                "relationship that stays significant here is better evidence of a genuine link "
                "between the two series.\n\n")
        f.write("\\input{" + f"tex_tables/regression_table_{cur_date}_detrended.tex" + "}\n\n")
        f.write("\\begin{figure}\n")
        f.write("\\centering\n")
        f.write("\\includegraphics[scale = 0.9]{" + f"plots/plot_{cur_date}_detrended.png" + "}\n")
        f.write("\\caption{Detrended Regression Plot for " + cur_date + "}\n")
        f.write("\\end{figure}\n")
        f.write("\\newpage\n")

def generate_series_info_latex(series: SeriesInfo) -> str:
    
    title = escape_latex(series.title)
    frequency = escape_latex(series.frequency)
    units = escape_latex(series.units)
    seasonal_adjustment = escape_latex(series.seasonal_adjustment)

    latex_str = f"\\noindent \\textbf{{Series ID: {series.id}}} \n\n"
    latex_str += f"\\noindent This series is titled {title} and has a frequency of {frequency}."
    latex_str += f" The units are {units} and the seasonal adjustment is {seasonal_adjustment}."
    latex_str += f"The observation start date is {series.observation_start} and the observation end date is {series.observation_end}."
    latex_str += f"The popularity of this series is {series.popularity}. \\\\ \n\n"

    return latex_str

