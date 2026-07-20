import sys
from data_format import *
from data_pull import *
from regressions import *
from tex_format import *
from ai_summary import generate_weekly_summary

def build_digest(cur_date, file_path, infos, regr, ai_summary_ok):
    lines = [f"## Daily run — {cur_date}", ""]

    lines.append("**Series pulled:**")
    for info in infos:
        lines.append(f"- `{info.id}` — {info.title}")
    lines.append("")

    x_col = regr.x_cols[cur_date][0]
    y_col = regr.y_col[cur_date]
    pval = float(regr.models[cur_date].pvalues[x_col])
    rsquared = float(regr.models[cur_date].rsquared)
    significance = "significant at the 5% level" if pval < 0.05 else "not significant at the 5% level"
    lines.append(f"**Regression (raw):** `{y_col}` on `{x_col}` — R² = {rsquared:.3f}, p = {pval:.3f} ({significance})")

    detrended_name = f"{cur_date}_detrended"
    d_x_col = regr.x_cols[detrended_name][0]
    d_pval = float(regr.models[detrended_name].pvalues[d_x_col])
    d_rsquared = float(regr.models[detrended_name].rsquared)
    d_significance = "significant at the 5% level" if d_pval < 0.05 else "not significant at the 5% level"
    lines.append(f"**Regression (detrended):** R² = {d_rsquared:.3f}, p = {d_pval:.3f} ({d_significance})")
    lines.append("")

    summary_status = "updated by Claude" if ai_summary_ok else "AI generation failed this run -- fallback disclaimer written instead"
    lines.append(f"**Weekly summary:** {summary_status}")
    lines.append(f"**Week folder:** `{file_path}`")

    return "\n".join(lines)

def main(cur_date, file_path, cur_week = None):
    raw, clean, infos = get_merged_dfs_dense([("fred", 2)], 20)

    regr = Regression_Wrapper(raw, clean, "date")
    regr.run_linear_regression(cur_date, [3], 4)
    regr.write_regression_results_to_csv(cur_date, f"{file_path}/regression_summaries.csv")
    regr.write_regression_latex(cur_date, f"{file_path}/tex_tables/regression_table_{cur_date}.tex")
    regr.save_plot_png(cur_date, f"{file_path}/plots/plot_{cur_date}.png")

    detrended_name = f"{cur_date}_detrended"
    regr.run_detrended_regression(detrended_name, [3], 4)
    regr.write_regression_results_to_csv(detrended_name, f"{file_path}/regression_summaries.csv")
    regr.write_regression_latex(detrended_name, f"{file_path}/tex_tables/regression_table_{detrended_name}.tex")
    regr.save_plot_png(detrended_name, f"{file_path}/plots/plot_{detrended_name}.png")

    if cur_week != None:
        init_folder_tex(file_path, cur_date)

    daily_tex_update(file_path, cur_date, infos)

    ai_summary_ok = generate_weekly_summary(file_path)

    digest = build_digest(cur_date, file_path, infos, regr, ai_summary_ok)
    with open("digest.txt", "w") as f:
        f.write(digest)

if __name__ == "__main__":
    # Read in arguments
    args = sys.argv[1:]  
    if len(args) > 2:
        main(args[0], args[1], args[2])
    else:
        main(args[0], args[1])