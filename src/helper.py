"""
Helpers for feature engineering and model evaluation
"""

from sklearn.metrics import mean_squared_error, r2_score

def evalute_model(model, dataset):
    """
    model: Trained Scikit-Learn model, anything that support a .predict() method
    dataset: Pandas Dataframe which has 8 columns for the coefficients and another
             column for the cateogry and another for the ke_ratio
    return: {"overall": {"mse": mse, "r2": r2}, "hetero": {"mse": mse, "r2": r2}, "hetero_excl_bist": {"mse": mse, "r2": r2}}
    """

    # Initialize lists to hold metrics
    overall_metrics = {"mse": 0, "r2": 0}
    hetero_metrics = {"mse": 0, "r2": 0}
    hetero_excl_bist_metrics = {"mse": 0, "r2": 0}

    # Calculate metrics on entire dataset
    X_test = dataset[["c2_A", "c2_B", "c2_C", "c2_D",
                      "c3_A", "c3_B", "c3_C", "c3_D",]]
    y_test = dataset[["KE_ratio"]]
    y_pred = model.predict(X_test)
    overall_metrics["mse"] = mean_squared_error(y_test, y_pred)
    overall_metrics["r2"] = r2_score(y_test, y_pred)

    # Calculate metrics on dataset for only hetero
    X_test = dataset[dataset["Category"] == "het"][["c2_A", "c2_B", "c2_C", "c2_D",
                                                    "c3_A", "c3_B", "c3_C", "c3_D",]]
    y_test = dataset[dataset["Category"] == "het"][["KE_ratio"]]
    y_pred = model.predict(X_test)
    hetero_metrics["mse"] = mean_squared_error(y_test, y_pred)
    hetero_metrics["r2"] = r2_score(y_test, y_pred)

    # Calculate metrics on dataset for only hetero_excl_bist
    X_test = dataset[dataset["Category"] == "het_excl_bist"][["c2_A", "c2_B", "c2_C", "c2_D",
                                                              "c3_A", "c3_B", "c3_C", "c3_D",]]
    y_test = dataset[dataset["Category"] == "het_excl_bist"][["KE_ratio"]]
    y_pred = model.predict(X_test)
    hetero_excl_bist_metrics["mse"] = mean_squared_error(y_test, y_pred)
    hetero_excl_bist_metrics["r2"] = r2_score(y_test, y_pred)

    return {"overall": overall_metrics, "hetero": hetero_metrics, "hetero_excl_bist": hetero_excl_bist_metrics}


def display_eval(model_eval_dict):
    """
    model_eval_dict: The output of evalute_model, a dict of the form
                     {"overall": {"mse": mse, "r2": r2}, 
                      "hetero": {"mse": mse, "r2": r2}, 
                      "hetero_excl_bist": {"mse": mse, "r2": r2}}
    return: Nothing, just prints out the evalution metrics
    """
    
    print("======================================================")
    print("Model Evaluation over all Data")
    print(f"MSE: {model_eval_dict['overall']['mse']}")
    print(f"R2:  {model_eval_dict['overall']['r2']}")
    print("======================================================\n\n")

    print("======================================================")
    print("Model Evaluation over all Heterogeneous Rows")
    print(f"MSE: {model_eval_dict['hetero']['mse']}")
    print(f"R2:  {model_eval_dict['hetero']['r2']}")
    print("======================================================\n\n")

    print("======================================================")
    print("Model Evaluation over all Heterogeneous Rows Excluding Bistability")
    print(f"MSE: {model_eval_dict['hetero_excl_bist']['mse']}")
    print(f"R2:  {model_eval_dict['hetero_excl_bist']['r2']}")
    print("======================================================\n\n")
    


