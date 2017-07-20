import AnnotatedArticle as aa
import pickle
import numpy as np
import scipy.stats as stats
import pylab as pl


def load_obj(name):
    with open(name, 'rb') as f:
        return pickle.load(f)


def calculate_kaw_scores(kinase_AA, axis_AA):
    k_score = kinase_AA.counter_of_hit_terms[rel_kinase] / wc_dict[doc]
    a_score = axis_AA.number_of_hits / wc_dict[doc]
    kaw_score = a_score * k_score
    return [k_score, a_score, kaw_score]


def calculate_min_proximity(kinase_AA, axis_AA):
    axis_tokens = []
    kinase_tokens = []
    axis_attribs = axis_AA.list_of_attrib_dicts
    kinase_attribs = [kin for kin in kinase_AA.list_of_attrib_dicts if kin['DictCanon'] == rel_kinase]
    for attrib in axis_attribs:
        for token in attrib['matchedTokens'].split(" "):
            axis_tokens.append(int(token))
    for attrib in kinase_attribs:
        for token in attrib['matchedTokens'].split(" "):
            kinase_tokens.append(int(token))
    min_proximity = 999999
    for k in kinase_tokens:
        for a in axis_tokens:
            dist = abs(k - a) / 10
            if dist < min_proximity:
                min_proximity = dist
    p_hist.append(min_proximity)
    return min_proximity


def process_doc(kinase, doc):
    axis_AA = load_obj(axis_input_dir + "/" + doc + ".txt.xmi.pkl")
    kinase_AA = load_obj(kinase_input_dir + "/" + doc + ".txt.xmi.pkl")
    kaw_scores = [0, 0, 0]
    min_proximity = 0

    kaw_scores = calculate_kaw_scores(kinase_AA, axis_AA)
    min_proximity = calculate_min_proximity(kinase_AA, axis_AA)

    try:
        metric_dict[kinase].append([doc] + kaw_scores + [min_proximity])
    except KeyError:
        metric_dict[kinase] = [[doc] + kaw_scores + [min_proximity]]


def plot_hist(h):
    h = sorted(h)
    fit = stats.norm.pdf(h, np.mean(h), np.std(h))
    pl.plot(h, fit, '-o')
    pl.hist(h, normed=True, bins='auto')
    pl.show()

if __name__ == "__main__":
    kinase_input_dir = r"C:\Users\Adam\Documents\MSU REU\FT_Post-Processed\AA_Sets\Kinase_DIS_Train_RW"
    axis_input_dir = r"C:\Users\Adam\Documents\MSU REU\FT_Post-Processed\AA_Sets\HP"
    predicted_dictionary_input = r"C:\Users\Adam\Documents\MSU REU\FT_Post-Processed\IR\FT_HP_IR.pkl"
    word_count_dictionary_input = r"C:\Users\Adam\Documents\MSU REU\FT_Post-Processed\IR\FT_wordcount.pkl"
    output_file = r"C:\Users\Adam\Documents\MSU REU\FT_Post-Processed\Features\FT_HP_Feat.pkl"
    axis_tokens = []
    kinase_tokens = []
    metric_dict = {}
    k_hist = []

    wc_dict = load_obj(word_count_dictionary_input)
    kcounter = 0
    a_hist = []
    ka_hist = []
    p_hist = []

    pred_dict = load_obj(predicted_dictionary_input)
    dcounter = 0

    for rel_kinase in pred_dict:
        kcounter += 1
        for doc in pred_dict[rel_kinase]:
            dcounter += 1
            if dcounter % 100 == 0:
                print(str(kcounter) + " " + str(dcounter))
            try:
                process_doc(rel_kinase, doc)
            except EOFError:
                pass
            except KeyError:
                pass
    with open(output_file, 'wb') as output_file:
        pickle.dump(metric_dict, output_file, pickle.HIGHEST_PROTOCOL)

