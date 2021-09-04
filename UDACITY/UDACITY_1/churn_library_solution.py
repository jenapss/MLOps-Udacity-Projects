# library doc string

"""
The Library Docstring

"""

# import libraries
from sklearn.metrics import plot_roc_curve, classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
import shap
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
IMG_PATH = 'UDACITY_1/images/'

def import_data(pth):
    """
    returns dataframe for the csv found at pth

        input:
                pth: a path to the csv
        output:
                df: pandas dataframe
    
    
    """
    return pd.read_csv(pth)


def perform_eda(df):
    """perform eda on df and save figures to images folder
    input:
            df: pandas dataframe

    output:
            None
    """

    df['Churn'] = df['Attrition_Flag'].apply(lambda val: 0 if val == "Existing Customer" else 1)
    fig1 = df['Churn'].hist().get_figure()
    fig1.savefig('IMG_PATH/1.jpg')
    
    fig2 = df['Customer_Age'].hist().get_figure()
    fig2.savefig('IMG_PATH/2.jpg')

    fig3 = df.Marital_Status.value_counts('normalize').plot(kind='bar').get_figure()
    fig3.savefig('IMG_PATH/3.jpg')

    fig4 = sns.distplot(df['Total_Trans_Ct']).get_figure()
    fig4.savefig('IMG_PATH/4.jpg')

    fig5 = sns.heatmap(df.corr(), annot=False, cmap='Dark2_r', linewidths = 2).get_figure()
    fig5.savefig('IMG_PATH/5.jpg')
    
    return None



def encoder_helper(df, category_lst): # deleted one argument
    '''
    helper function to turn each categorical column into a new column with
    propotion of churn for each category - associated with cell 15 from the notebook

    input:
            df: pandas dataframe
            category_lst: list of columns that contain categorical features
            response: string of response name [optional argument that could be used for naming variables or index y column]

    output:
            df: pandas dataframe with new columns for
    '''
    for category in category_lst:
        lst = []
        groups = df.groupby(category).mean()['Churn']

        for val in df[category]:
            lst.append(groups.loc[val])
        df['{}_Churn'.format(category)] = lst
    
    return df




def perform_feature_engineering(df,response): 
    '''
    input:
              df: pandas dataframe
              response: string of response name [optional argument that could be used for naming variables or index y column]

    output:
              X_train: X training data
              X_test: X testing data
              y_train: y training data
              y_test: y testing data
    '''
    # drop unneeded columns in simpler way than manually listing all needed columns.
    keep_cols = df.drop(['CLIENTNUM', 'Churn'], axis=1, inplace=True)
    
    X = df[keep_cols]
    y = df[response]

    # train test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.3, random_state=42)
    
    return X_train, X_test, y_train, y_test


def model():

    """
    Model Initialization

    input: None

    output: cv_rfc, lrc 
                
                cv_rfc - Cross validation of Random Forest Classifier model
                lrc - Logistic Regression model

    """

    rfc = RandomForestClassifier(random_state=42)
    lrc = LogisticRegression()

    param_grid = {
        'n_estimators' : [200,500],
        'max_features' : ['auto', 'sqrt'],
        'max_depth' : [4,5,100],
        'criterion' : ['gini', 'entropy']
    }

    cv_rfc = GridSearchCV(estimator=rfc, param_grid=param_grid,cv=5)
    return cv_rfc, lrc
    


def train_models(X_train, X_test, y_train, y_test):
    '''
    train, store model results: images + scores, and store models
    input:
              X_train: X training data
              X_test: X testing data
              y_train: y training data
              y_test: y testing data
    output:
              None
    '''
    # grid search
    cv_randomforest, log_reg = model()
    cv_randomforest.fit(X_train, y_train)

    log_reg.fit(X_train, y_train)

    y_train_preds_rf = cv_randomforest.best_estimator_.predict(X_train)
    y_test_preds_rf = cv_randomforest.best_estimator_.predict(X_test)

    y_train_preds_lr = log_reg.predict(X_train)
    y_test_preds_lr = log_reg.predict(X_test)

    # scores
    print('RANDOM FOREST RESULTS \n')

    print('TEST RESULTS \n', classification_report(y_test, y_test_preds_rf))
    print('TRAIN RESULTS \n', classification_report(y_train, y_train_preds_rf))

    print('LOGREG RESULTS \n')

    print('TEST RESULTS \n', classification_report(y_test, y_test_preds_lr))
    print('TRAIN RESULTS \n', classification_report(y_train, y_train_preds_lr))
    

    # ----- PLOTS ----- PLOTS ---- 

    # logistics regression results
    lrc_plot = plot_roc_curve(log_reg,X_test,y_test)
    plt.savefig('./images/result1.png')

    # random forest regression results

    plt.figure(figsize=(15,8))
    ax = plt.gca()
    plot_roc_curve(cv_randomforest.best_estimator_, X_test, y_test, ax=ax, alpha=0.8)

    lrc_plot.plot(ax=ax, alpha=0.8)
    plt.savefig('./images/results2.png')


    # save the best model
    joblib.dump(cv_randomforest.best_estimator_, './models/rfc_model.pkl')
    joblib.dump(log_reg, './models/logistic_model.pkl')
        
    return None
    

def feature_importance_plot(model, X_data, output_pth):
    '''
    creates and stores the feature importances in pth
    input:
            model: model object containing feature_importances_
            X_data: pandas dataframe of X values
            output_pth: path to store the figure

    output:
             None

    '''

    # LOAD THE MODEL
    cv_randomforest = joblib.load('./models/rfc_model.pkl')


    # END LOADING THE MODEL
    explainer = shap.TreeExplainer(cv_randomforest.best_estimator_)
    shap_values = explainer.shap_values(X_data)
    shap.summary_plot(shap_values, X_data, plot_type = 'bar')
    # save plot
    plt.savefig('./images/results3.png')



    # Calculate feature importances
    importances = cv_randomforest.best_estimator_.feature_importances_
    #Sort feature importances in descending order
    indices = np.argsort(importances)[::-1]
    # Rearrange feature names so they match the sorted feature names
    names = [X_data.columns[i] for i in indices]

    # Create a plot and save it
    plt.figure(figsize=(20,5))
    plt.title('Feature Importances')
    plt.ylabel('Importance')
    # Add bars
    plt.bar(range(X_data.shape[1]), importances[indices])
    # Add feature names as x-axis labels
    plt.xticks(range(X_data.shape[1]), names, rotation = 90)
    plt.savefig('./images/results4.png')

    return None


def classification_report_image(y_train,
                                y_test,
                                y_train_preds_lr,
                                y_train_preds_rf,
                                y_test_preds_lr,
                                y_test_preds_rf):
    '''
    produces classification report for training and testing results and stores report as image
    in images folder
    input:
            y_train: training response values
            y_test:  test response values
            y_train_preds_lr: training predictions from logistic regression
            y_train_preds_rf: training predictions from random forest
            y_test_preds_lr: test predictions from logistic regression
            y_test_preds_rf: test predictions from random forest

    output:
             None
    '''
    plt.rc('figure', figsize=(5, 5))
    #plt.text(0.01, 0.05, str(model.summary()), {'fontsize': 12}) old approach
    plt.text(0.01, 1.25, str('Random Forest Train'), {'fontsize': 10}, fontproperties = 'monospace')
    plt.text(0.01, 0.05, str(classification_report(y_test, y_test_preds_rf)), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
    plt.text(0.01, 0.6, str('Random Forest Test'), {'fontsize': 10}, fontproperties = 'monospace')
    plt.text(0.01, 0.7, str(classification_report(y_train, y_train_preds_rf)), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
    plt.axis('off')
    plt.savefig('./images/last_result.png')


    plt.rc('figure', figsize=(5, 5))
    plt.text(0.01, 1.25, str('Logistic Regression Train'), {'fontsize': 10}, fontproperties = 'monospace')
    plt.text(0.01, 0.05, str(classification_report(y_train, y_train_preds_lr)), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
    plt.text(0.01, 0.6, str('Logistic Regression Test'), {'fontsize': 10}, fontproperties = 'monospace')
    plt.text(0.01, 0.7, str(classification_report(y_test, y_test_preds_lr)), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
    plt.axis('off')
    plt.savefig('./images/last_result2.png')





