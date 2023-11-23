import pandas as pd
import os
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt

# import openpyxl
# from openpyxl import load_workbook
from collections import defaultdict


# Metrics OCR
def avg_wer(wer_scores, combined_ref_len):
    return float(sum(wer_scores)) / float(combined_ref_len)


def _levenshtein_distance(ref, hyp):
    m = len(ref)
    n = len(hyp)

    # special case
    if ref == hyp:
        return 0
    if m == 0:
        return n
    if n == 0:
        return m

    if m < n:
        ref, hyp = hyp, ref
        m, n = n, m

    # use O(min(m, n)) space
    distance = np.zeros((2, n + 1), dtype=np.int32)

    # initialize distance matrix
    for j in range(0, n + 1):
        distance[0][j] = j

    # calculate levenshtein distance
    for i in range(1, m + 1):
        prev_row_idx = (i - 1) % 2
        cur_row_idx = i % 2
        distance[cur_row_idx][0] = i
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                distance[cur_row_idx][j] = distance[prev_row_idx][j - 1]
            else:
                s_num = distance[prev_row_idx][j - 1] + 1
                i_num = distance[cur_row_idx][j - 1] + 1
                d_num = distance[prev_row_idx][j] + 1
                distance[cur_row_idx][j] = min(s_num, i_num, d_num)

    return distance[m % 2][n]


def word_errors(reference, hypothesis, ignore_case=False, delimiter=" "):
    if ignore_case == True:
        reference = reference.lower()
        hypothesis = hypothesis.lower()

    ref_words = reference.split(delimiter)
    hyp_words = hypothesis.split(delimiter)

    edit_distance = _levenshtein_distance(ref_words, hyp_words)
    return float(edit_distance), len(ref_words)


def char_errors(reference, hypothesis, ignore_case=False, remove_space=False):
    if ignore_case == True:
        reference = reference.lower()
        hypothesis = hypothesis.lower()

    join_char = " "
    if remove_space == True:
        join_char = ""

    reference = join_char.join(filter(None, reference.split(" ")))
    hypothesis = join_char.join(filter(None, hypothesis.split(" ")))

    edit_distance = _levenshtein_distance(reference, hypothesis)
    return float(edit_distance), len(reference)


def wer(reference, hypothesis, ignore_case=False, delimiter=" "):
    edit_distance, ref_len = word_errors(reference, hypothesis, ignore_case, delimiter)
    if ref_len == 0:
        raise ValueError("Reference's word number should be greater than 0.")

    wer = float(edit_distance) / ref_len
    return wer


def cer(reference, hypothesis, ignore_case=False, remove_space=False):
    edit_distance, ref_len = char_errors(
        reference, hypothesis, ignore_case, remove_space
    )
    if ref_len == 0:
        raise ValueError("Length of reference should be greater than 0.")

    cer = float(edit_distance) / ref_len
    return cer


def lexicon_search(hypo, dic):
    dis_list = []
    index = 0
    for i in range(len(dic)):
        dic[i] = str(dic[i])
        distance = _levenshtein_distance(hypo.lower(), dic[i].lower())

        dis_list.append(distance)
        if distance == min(dis_list):
            index = i
    return index, dic[index], distance


# Excel
def read_answer(path):
    data = pd.read_excel(path)
    header = data.columns.values
    # print(header)
    answer = {}
    for i in range(len(header)):
        a = defaultdict(list)
        b = data.iloc[:, i].to_list()
        for j in range(len(b)):
            a[j + 1].append(b[j])
        answer[str(header[i])] = a
    return answer


def class_list(dataPath):
    data = pd.read_excel(dataPath)
    MSSV_list = data.iloc[:, 0].to_list()
    Ho_list = data.iloc[:, 1].to_list()
    Ten_list = data.iloc[:, 2].to_list()
    name_MSSV_list = []
    name_list = []

    MSSV_list = [str(i) for i in MSSV_list]
    for i in MSSV_list:
        MSSV_list[MSSV_list.index(i)] = "0" * (6 - len(i)) + i

    for i in range(len(Ho_list)):
        name_list.append(str(Ho_list[i] + " " + Ten_list[i]))
        name_MSSV_list.append(
            str(Ho_list[i] + " " + Ten_list[i] + " " + str(MSSV_list[i]))
        )
    return name_list, MSSV_list, name_MSSV_list


# def writing_to_excel(path, score):
#     wb = openpyxl.load_workbook(path, read_only=False, keep_vba=False)
#     ws = wb[wb.sheetnames[0]]
#     index = score[0] + 2
#     index_C = "E" + str(index)
#     index_I = "F" + str(index)
#     index_S = "G" + str(index)
#     ws[index_C] = score[1]
#     ws[index_I] = 50 - score[1]
#     ws[index_S] = score[2]

#     wb.save(path)
