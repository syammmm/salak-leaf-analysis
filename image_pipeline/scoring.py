def minmax(x, xmin, xmax):
    return max(0, min(1, (x - xmin) / (xmax - xmin)))


def compute_visual_score(features):
    ExG_n = minmax(features["mean_ExG"], -50, 200)
    GLI_n = minmax(features["mean_GLI"], -0.2, 0.6)
    G_n   = minmax(features["mean_G"], 60, 160)

    score_01 = (
        0.45 * ExG_n +
        0.35 * GLI_n +
        0.20 * G_n
    )

    score = round(score_01 * 100, 1)

    if score >= 80:
        label = "Sehat"
    elif score >= 60:
        label = "Cukup Sehat"
    elif score >= 40:
        label = "Kurang Sehat"
    else:
        label = "Stres"

    return {
        "score": score,
        "label": label
    }