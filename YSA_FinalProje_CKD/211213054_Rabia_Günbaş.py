import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
from ucimlrepo import fetch_ucirepo
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns

chronic_kidney_disease = fetch_ucirepo(id=336)

X = chronic_kidney_disease.data.features
y = chronic_kidney_disease.data.targets

categorical_columns = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']

X_numeric = X.select_dtypes(include=['float64', 'int64'])
X_categorical = X[categorical_columns]


numerical_columns = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wbcc', 'rbcc']
X_numeric.loc[:, numerical_columns] = X_numeric[numerical_columns].fillna(X_numeric[numerical_columns].median())

X_categorical = pd.get_dummies(X_categorical)


X = pd.concat([X_numeric, X_categorical], axis=1)

selected_columns = ['cad_yes', 'htn_yes', 'ba_present']
X = X[selected_columns]


y = y.values.ravel()
y = pd.Series(y).str.strip().values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.34, random_state=None)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


smote = SMOTE(random_state=None)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)


root = tk.Tk()
root.title("MLP Classifier - Chronic Kidney Disease")


hidden_layers_label = tk.Label(root, text="Hidden Layer Sizes (comma-separated):")
hidden_layers_label.grid(row=0, column=0)
hidden_layers_entry = tk.Entry(root)
hidden_layers_entry.grid(row=0, column=1)


max_iter_label = tk.Label(root, text="Max Iterations:")
max_iter_label.grid(row=1, column=0)
max_iter_entry = tk.Entry(root)
max_iter_entry.grid(row=1, column=1)


def run_model():
    hidden_layer_sizes = tuple(map(int, hidden_layers_entry.get().split(',')))
    max_iter = int(max_iter_entry.get())
    mlp = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, max_iter=max_iter, random_state=None)
    mlp.fit(X_train_balanced, y_train_balanced)
    y_pred = mlp.predict(X_test)
    report = classification_report(y_test, y_pred)
    matrix = confusion_matrix(y_test, y_pred)

    messagebox.showinfo("Classification Report", f"{report}\n\nConfusion Matrix:\n{matrix}")
    print("Classification Report:\n", report)
    print("Confusion Matrix:\n", matrix)

    cv_scores_5 = cross_val_score(mlp, X, y, cv=StratifiedKFold(n_splits=5, random_state=None, shuffle=True))
    cv_scores_10 = cross_val_score(mlp, X, y, cv=StratifiedKFold(n_splits=10, random_state=None, shuffle=True))
    cv_result = f"5-Fold Cross-Validation Mean: {np.mean(cv_scores_5)}\n10-Fold Cross-Validation Mean: {np.mean(cv_scores_10)}"
    messagebox.showinfo("Cross Validation Results", cv_result)

    print("5-Fold Cross-Validation Mean:", np.mean(cv_scores_5))
    print("10-Fold Cross-Validation Mean:", np.mean(cv_scores_10))

    plt.figure(figsize=(6, 4))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', xticklabels=np.unique(y), yticklabels=np.unique(y))
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

    plt.plot(np.arange(len(mlp.loss_curve_)), mlp.loss_curve_, label='Training Loss')
    plt.title('MLP Training Loss Curve')
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

run_button = tk.Button(root, text="Run Model", command=run_model)
run_button.grid(row=2, column=0, columnspan=2)

root.mainloop()

param_grid = {
    'hidden_layer_sizes': [(50,), (100,), (150,), (50, 50), (100, 50)],
    'max_iter': [ 500, 1000],
    'activation': ['relu', 'tanh', 'logistic', 'identity'],
}

mlp = MLPClassifier(solver='adam', random_state=None, max_iter=1000, learning_rate_init=0.001, tol=1e-4)
grid_search = GridSearchCV(mlp, param_grid, cv=5)
grid_search.fit(X_train_balanced, y_train_balanced)


best_params = grid_search.best_params_
best_model = grid_search.best_estimator_
print("En iyi parametreler:", best_params)
print("En iyi model:", best_model)