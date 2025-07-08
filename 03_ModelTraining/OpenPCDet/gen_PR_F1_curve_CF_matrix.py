import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, precision_recall_curve, average_precision_score, f1_score
from sklearn.preprocessing import label_binarize
import seaborn as sns



def read_prediction_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    pred_score = None
    pred_label = None
    frame_id = None

    for line in lines:
        if line.startswith('score:'):
            pred_score = float(line.split('[')[1].split(']')[0])
        elif line.startswith('pred_labels:'):
            pred_label = int(line.split('[')[1].split(']')[0])
        elif line.startswith('frame_id:'):
            frame_id = line.split(':')[1].strip()

    return frame_id, pred_label, pred_score


def read_ground_truth_file(file_path):
    with open(file_path, 'r') as f:
        line = f.readline().strip()

    parts = line.split()
    return parts[-1]  # The last element is the category name


def generate_metrics(pred_dir, gt_dir, classes):
    y_true = []
    y_pred = []
    y_scores = []

    class_to_index = {cls: idx for idx, cls in enumerate(classes)}

    for pred_file in os.listdir(pred_dir):
        if pred_file.endswith('.txt'):
            frame_id, pred_label, pred_score = read_prediction_file(os.path.join(pred_dir, pred_file))

            gt_file = f"{frame_id}.txt"
            gt_path = os.path.join(gt_dir, gt_file)

            if os.path.exists(gt_path):
                gt_class = read_ground_truth_file(gt_path)

                y_true.append(class_to_index[gt_class])
                y_pred.append(pred_label - 1)  # Assuming pred_labels start from 1
                y_scores.append([pred_score if i == (pred_label - 1) else 0 for i in range(len(classes))])

    # Convert to numpy arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_scores = np.array(y_scores)

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred, normalize='true')

    # Binarize the output for PR curves
    y_true_bin = label_binarize(y_true, classes=range(len(classes)))

    # Compute PR curve, average precision, and F1 scores for each class
    precision = dict()
    recall = dict()
    average_precision = dict()
    f1_scores = dict()
    thresholds = dict()
    for i in range(len(classes)):
        precision[i], recall[i], thresholds[i] = precision_recall_curve(y_true_bin[:, i], y_scores[:, i])
        average_precision[i] = average_precision_score(y_true_bin[:, i], y_scores[:, i])
        f1_scores[i] = [f1_score(y_true_bin[:, i], y_scores[:, i] >= threshold) for threshold in thresholds[i]]

    # Compute micro-average PR curve and average precision
    precision["micro"], recall["micro"], thresholds["micro"] = precision_recall_curve(y_true_bin.ravel(),
                                                                                      y_scores.ravel())
    average_precision["micro"] = average_precision_score(y_true_bin, y_scores, average="micro")
    f1_scores["micro"] = [f1_score(y_true_bin.ravel(), y_scores.ravel() >= threshold, average="micro") for threshold in
                          thresholds["micro"]]

    return cm, precision, recall, average_precision, f1_scores, thresholds


def plot_confusion_matrix(cm, classes):
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='.2f', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.close()


def plot_pr_and_f1_curves(precision, recall, average_precision, f1_scores, thresholds, classes):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    # Plot PR curves
    for i, color in zip(range(len(classes)), plt.cm.rainbow(np.linspace(0, 1, len(classes)))):
        ax1.plot(recall[i], precision[i], color=color, lw=2,
                 label=f'{classes[i]} (AP = {average_precision[i]:0.2f})')

    ax1.plot(recall["micro"], precision["micro"], color='gold', lw=2,
             label=f'Micro-average (AP = {average_precision["micro"]:0.2f})')

    ax1.set_xlabel('Recall', fontsize=18)
    ax1.set_ylabel('Precision', fontsize=18)
    ax1.set_title('Precision-Recall Curves', fontsize=18)
    ax1.legend(loc="lower left", fontsize=16)
    ax1.grid(True)
    ax1.tick_params(axis='both', labelsize=16)

    # Plot F1 curves
    for i, color in zip(range(len(classes)), plt.cm.rainbow(np.linspace(0, 1, len(classes)))):
        ax2.plot(thresholds[i], f1_scores[i], color=color, lw=2, label=f'{classes[i]}')

    ax2.plot(thresholds["micro"], f1_scores["micro"], color='gold', lw=2, label='Micro-average')

    ax2.set_xlabel('Threshold', fontsize=18)
    ax2.set_ylabel('F1 Score', fontsize=18)
    ax2.set_title('F1 Scores vs Threshold', fontsize=18)
    ax2.legend(loc="lower left", fontsize=16)
    ax2.grid(True)
    ax2.tick_params(axis='both', labelsize=16)

    plt.tight_layout()
    plt.savefig('pr_and_f1_curves.png', dpi=400)
    plt.close()


# Main execution
pred_dir = '/home/dartagnan-dev/sahil-dev/Results/OpenPCdet/Radar_Static/txt_results'
gt_dir = '/home/dartagnan-dev/sahil-dev/Results/OpenPCdet/Radar_Static/labels'
classes = ['forklift+KLT', 'forklift', 'workstation', 'robotnik']

cm, precision, recall, average_precision, f1_scores, thresholds = generate_metrics(pred_dir, gt_dir, classes)
plot_confusion_matrix(cm, classes)
plot_pr_and_f1_curves(precision, recall, average_precision, f1_scores, thresholds, classes)

print("Confusion Matrix, Precision-Recall Curves, and F1 Curves have been saved as PNG files.")