import json
import os
import numpy as np
import csv


# global variable
# BERT_CLOTH_model
# BERT_DGen_model1
# BERT_CLOTH_DGen_model1
MODEL_NAME = "BERT_CLOTH_model"
RESULT_NAME = "dis_result_" + MODEL_NAME + ".json"


def main():
    result_path = os.path.join("./results/", RESULT_NAME)
    print(f"Reading result at {result_path}...")
    with open(result_path, "r") as file:
        results = json.load(file)

    print("Evaluating...")
    avg_eval = eval = {"P@1": 0.0, "P@3": 0.0, "R@3": 0.0, "F1@3": 0.0, "MRR": 0.0, "NDCG@10": 0.0}
    for result in results:
        eval = evaluate(result)
        for k in avg_eval.keys():
            avg_eval[k] += eval[k]

    for k in avg_eval.keys():
        avg_eval[k] /= len(results)

    # print(avg_eval)

    print("Save to csv file...")
    with open(f"./evaluations/evaluation_{MODEL_NAME}.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        for k in avg_eval.keys():
            writer.writerow([k, avg_eval[k]*100])

    for k in avg_eval.keys():
        print(f"{k}: {avg_eval[k]*100}%")

    print("Done!")


def evaluate(result):
    eval = {"P@1": 0.0, "P@3": 0.0, "R@3": 0.0, "F1@3": 0.0, "MRR": 0.0, "NDCG@10": 0.0}
    distractors = [d.lower() for d in result["distractors"]]
    generations = result["generations"]

    relevants = [int(generation in distractors) for generation in generations]
    # print(relevants)

    # P@1
    if relevants[0] == 1:
        eval["P@1"] = 1
    else:
        eval["P@1"] = 0

    # P@3
    eval["P@3"] = relevants[:3].count(1) / 3

    # R@3
    eval["R@3"] = relevants[:3].count(1) / 3

    # F1@3
    try:
        eval["F1@3"] = (2 * eval["P@3"] * eval["R@3"]) / (eval["P@3"] + eval["R@3"])
    except ZeroDivisionError:
        eval["F1@3"] = 0
    
    # MRR
    for i in range(len(relevants)):
        if relevants[i] == 1:
            eval["MRR"] = 1 / (i+1)
            break
    
    # NDCG@10
    eval["NDCG@10"] = ndcg_at_k(relevants, 10)

    return eval


def dcg_at_k(r, k):
    r = np.asfarray(r)[:k]
    if r.size:
        return r[0] + np.sum(r[1:] / np.log2(np.arange(2, r.size + 1)))
    return 0.


def ndcg_at_k(r, k):
    idcg = dcg_at_k(sorted(r, reverse=True), k)
    if not idcg:
        return 0.
    return dcg_at_k(r, k) / idcg


if __name__ == "__main__":
    main()