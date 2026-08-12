---
name: data-topic-plotting
description: Handle data-analysis plotting requests and HTML result reports, especially experiment comparisons where charts must make differences visible. Use when the user asks for data topic processing, plotting, visualization, data analysis, HTML reports, tables plus charts, grouped experiment plots, HN/RN validation summaries, intercept/filter curves, operational metric comparisons, broken axes, truncated axes, compressed axes, zoomed y-axes, or clearer visual comparison.
---

# Data Topic Plotting

Use this skill to turn a data question into a readable report. Start from the comparison the user wants to see, then choose tables and charts that expose the signal instead of hiding it behind irrelevant scale.

## Workflow

1. Identify the data topic: what groups, runs, metrics, and validation basis the user is comparing.
2. Confirm the accepted data basis from the request. If the user says only `120k`, never fill gaps with `40k`, debug, stale, or partial metrics.
3. Build a table first with raw counts, percentages, and missing markers. The chart should be explainable from the table.
4. Choose chart families around the question, not around the easiest plot to draw.
5. Render as HTML when the user is reviewing experiment results or asks for comfortable viewing.
6. Visually inspect the rendered report and revise any chart whose important movement still looks flat.

## Chart Rules

For line charts, do not default to a zero y-axis when all values sit far above zero and the useful signal is local movement. Use one of these policies:

- **Zoomed y-axis**: plot from the observed min/max plus padding when zero is not required.
- **Broken y-axis**: cut out unused ranges when raw-count lines must stay in one figure but baselines differ.
- **Small multiples**: split panels by metric with aligned x-axis and independent y-axis when scales differ.
- **Normalized delta/index**: use baseline-relative movement when comparing curve shape, and keep raw values in the table.

Always label a truncated, broken, compressed, zoomed, or normalized axis. Visual clarity must not become silent distortion.

## Large-Baseline Counts

When plotting counts such as intercepted defects around one range and filtered normals around a much larger range:

- Do not use one unbroken shared y-axis that makes both lines look flat.
- If the user asks for one chart with two lines, use a broken/compressed axis, dual aligned panels, or normalized deltas with a raw-count table.
- If the top metrics and bottom metrics differ greatly, shorten the unused middle of the axis or split the panels.
- If the visual span on a zero baseline would occupy less than about 25% of chart height, revise the axis policy.

## Grouping Defaults

Prefer the grouping the user named:

- Plot HN1 points together when the user asks for HN1's 20 points.
- Plot HN2 points together when the user asks for HN2's 10 points.
- Put random/control experiments in a separate chart unless the user asks for direct overlay.
- Avoid crowded multi-line figures when separate charts answer the question more clearly.
- Keep each chart focused: one question, a small number of lines, and a nearby raw table.

## YOLO-CV HN/RN Defaults

For Stage-1 HN/RN operational reports:

- Use `intercept_defect` as TP and `filter_normal` as TN for intercept/filter count charts.
- Use `miss_defect` as FN and `false_pass_normal` as FP for error count charts.
- Higher is better for recall/intercept metrics. Lower is better for FPR/pass-through metrics.
- Mark missing runs explicitly as `MISSING`; do not interpolate or substitute other validation sizes.
- Include both count and rate columns when available so the user can judge magnitude and ratio.

## Visual QA

Before delivery:

- Open or screenshot the HTML/chart when possible.
- Check that lines visibly move where values differ.
- Check legends, axis labels, table text, and titles do not overlap.
- If the user would see a flat line while the table has meaningful differences, redraw with a zoomed, broken, split, or normalized axis.
