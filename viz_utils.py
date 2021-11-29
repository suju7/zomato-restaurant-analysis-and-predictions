"""
Script created to consolidate useful functions used in plotting and customizing graphics
"""

"""
--------------------------------------------
---------- IMPORTING LIBRARIES ----------
--------------------------------------------
"""
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from warnings import filterwarnings
filterwarnings('ignore')
from typing import *
from dataclasses import dataclass
from math import ceil

"""
--------------------------------------------
---------- 1. AXIS FORMATTING ----------
--------------------------------------------
"""


# Formatting matplotlib axes
def format_spines(ax, right_border=True):
    """
    This function sets up borders from an axis and personalize colors

    Input:
        Axis and a flag for deciding or not to plot the right border
    Returns:
        Plot configuration
    """
    # Setting up colors
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['top'].set_visible(False)
    if right_border:
        ax.spines['right'].set_color('#CCCCCC')
    else:
        ax.spines['right'].set_color('#FFFFFF')
    ax.patch.set_facecolor('#FFFFFF')

# Class for plotting data labels on bar charts
# Reference: https://towardsdatascience.com/annotating-bar-charts-and-other-matplolib-techniques-cecb54315015
Patch = matplotlib.patches.Patch
PosVal = Tuple[float, Tuple[float, float]]
Axis = matplotlib.axes.Axes
PosValFunc = Callable[[Patch], PosVal]

@dataclass
class AnnotateBars:
    font_size: int = 10
    color: str = "black"
    n_dec: int = 2
    def horizontal(self, ax: Axis, centered=False):
        def get_vals(p: Patch) -> PosVal:
            value = p.get_width()
            div = 2 if centered else 1
            pos = (
                p.get_x() + p.get_width() / div,
                p.get_y() + p.get_height() / 2,
            )
            return value, pos
        ha = "center" if centered else  "left"
        self._annotate(ax, get_vals, ha=ha, va="center")
    def vertical(self, ax: Axis, centered:bool=False):
        def get_vals(p: Patch) -> PosVal:
            value = p.get_height()
            div = 2 if centered else 1
            pos = (p.get_x() + p.get_width() / 2,
                   p.get_y() + p.get_height() / div
            )
            return value, pos
        va = "center" if centered else "bottom"
        self._annotate(ax, get_vals, ha="center", va=va)
    def _annotate(self, ax, func: PosValFunc, **kwargs):
        cfg = {"color": self.color,
               "fontsize": self.font_size, **kwargs}
        for p in ax.patches:
            value, pos = func(p)
            ax.annotate(f"{value:.{self.n_dec}f}", pos, **cfg)

# Defining useful functions for plotting labels on the graph
def make_autopct(values):
    """
    Phases:
         1. definition of function for formatting labels

     Arguments:
         values -- values extracted from the value_counts() function of the analysis column [list]

     Return:
         my_autopct -- formatted string for plotting labels
    """

    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))

        return '{p:.1f}%\n({v:d})'.format(p=pct, v=val)

    return my_autopct

"""
--------------------------------------------
---------- 2. GRAPHIC PLOTS -----------
--------------------------------------------
"""


# Function for plotting a donut graph against a specific dataset variable
def donut_plot(df, col, ax, label_names=None, text='', colors=['crimson', 'navy'], circle_radius=0.8,
            title=f'Thread Graph', flag_ruido=0):
    """
    Phases:
         1. definition of useful functions to show labels in absolute value and percentage
         2. creation of figure and central circle of predefined radius
         3. pie chart plot and center circle addition
         4. final plot setup

     Arguments:
         df -- DataFrame target of analysis [pandas.DataFrame]
         col -- DataFrame column to parse [string]
         label_names -- custom names to be plotted as labels [list]
         text -- central text to be placed [string / default: '']
         colors -- input colors [list / default: ['crimson', 'navy']]
         figsize -- plot dimensions [tuple / default: (8, 8)]
         circle_radius -- radius of the center circle [float / default: 0.8]

     Return:
         None
    """

    # Return of values and definition of the figure
    values = df[col].value_counts().values
    if label_names is None:
        label_names = df[col].value_counts().index

    # Checking suppression parameter of any analysis category
    if flag_ruido > 0:
        values = values[:-flag_ruido]
        label_names = label_names[:-flag_ruido]

    # Plotting thread graph
    center_circle = plt.Circle((0, 0), circle_radius, color='white')
    ax.pie(values, labels=label_names, colors=colors, autopct=make_autopct(values))
    ax.add_artist(center_circle)

    # Setting core text arguments
    kwargs = dict(size=20, fontweight='bold', va='center')
    ax.text(0, 0, text, ha='center', **kwargs)
    ax.set_title(title, size=14, color='dimgrey')


# Function for analysis of the correlation matrix
def target_correlation_matrix(data, label_name, ax, n_vars=10, corr='positive', fmt='.2f', cmap='YlGnBu',
                              cbar=True, annot=True, square=True):
    """
    Phases:
         1. construction of correlation between variables
         2. filtering of the top k variables with the highest correlation
         3. plotting and configuring the correlation matrix

     Arguments:
         data -- DataFrame to parse [pandas.DataFrame]
         label_name -- name of the column containing the response variable [string]
         n_vars -- indicator of the top k variables to be analyzed [int]
         corr -- Boolean indicator for plotting correlations ('positive', 'negative') [string]
         fmt -- format of correlation numbers in plot [string]
         cmap -- color mapping [string]
         figsize -- graphical plot dimensions [tuple]
         cbar -- side indicator bar plot indicator [bool]
         annot -- annotation indicator of correlation numbers in matrix [bool]
         square -- indicator for quadratic matrix resizing [bool]

     Return:
         None
    """

    corr_mx = data.corr()

    if corr == 'positive':
        corr_cols = list(corr_mx.nlargest(n_vars+1, label_name)[label_name].index)
        title = f'Top {n_vars} Features - Correlação Positiva com o Target'
    elif corr == 'negative':
        corr_cols = list(corr_mx.nsmallest(n_vars+1, label_name)[label_name].index)
        corr_cols = [label_name] + corr_cols[:-1]
        title = f'Top {n_vars} Features - Correlação Negativa com o Target'
        cmap = 'magma'

    corr_data = np.corrcoef(data[corr_cols].values.T)

    sns.heatmap(corr_data, ax=ax, cbar=cbar, annot=annot, square=square, fmt=fmt, cmap=cmap,
                yticklabels=corr_cols, xticklabels=corr_cols)
    ax.set_title(title, size=14, color='dimgrey', pad=20)

    return


# Distplot for feature density comparison based on the target variable
def distplot(df, features, fig_cols, hue=False, color=['crimson', 'darkslateblue'], hist=False, figsize=(16, 12)):
    """
    Phases:
         1. creation of figure according to argument specifications
         2. loop for boxplot plot by axis
         3. graphic formatting
         4. validation of surplus axes

     Arguments:
         df -- database for plotting [pandas.DataFrame]
         features -- set of columns to be evaluated [list]
         fig_cols -- matplotlib figure specifications [int]
         hue -- response variable contained in base [string -- default: False]
         color_list -- colors for each class in the charts [list - default: ['crimson', 'darkslateblue']]
         hist -- histogram range plot indicator [bool - default: False]
         figsize -- plot dimensions [tuple - default: (16, 12)]

     Return:
         None
    """

    n_features = len(features)
    fig_cols = fig_cols
    fig_rows = ceil(n_features / fig_cols)
    i, j, color_idx = (0, 0, 0)

    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=figsize)

    for col in features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]
        target_idx = 0

        if hue != False:
            for classe in df[hue].value_counts().index:
                df_hue = df[df[hue] == classe]
                sns.distplot(df_hue[col], color=color[target_idx], hist=hist, ax=ax, label=classe)
                target_idx += 1
        else:
            sns.distplot(df[col], color=color, hist=hist, ax=ax)

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

        ax.set_title(f'Feature: {col}', color='dimgrey', size=14)
        plt.setp(ax, yticks=[])
        sns.set(style='white')
        sns.despine(left=True)

    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        if n_plots >= n_features:
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    plt.tight_layout()
    plt.show()

# Stripplot plotting function
def stripplot(df, features, fig_cols, hue=False, palette='viridis', figsize=(16, 12)):
    """
    Phases:
         1. creation of figure according to argument specifications
         2. loop for stripplot plot by axis
         3. graphic formatting
         4. validation of surplus axes

     Arguments:
         df -- database for plotting [pandas.DataFrame]
         features -- set of columns to be evaluated [list]
         fig_cols -- matplotlib figure specifications [int]
         hue -- response variable contained in base [string - default: False]
         palette -- color palette [string / list - default: 'viridis']
         figsize -- plot figure dimensions [tuple - default: (16, 12)]

     Return:
         None    """

    n_features = len(features)
    fig_cols = fig_cols
    fig_rows = ceil(n_features / fig_cols)
    i, j, color_idx = (0, 0, 0)

    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=figsize)

    for col in features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]

        if hue != False:
            sns.stripplot(x=df[hue], y=df[col], ax=ax, palette=palette)
        else:
            sns.stripplot(y=df[col], ax=ax, palette=palette)

        format_spines(ax, right_border=False)
        ax.set_title(f'Feature: {col.upper()}', size=14, color='dimgrey')
        plt.tight_layout()

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        if n_plots >= n_features:
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        j += 1
        if j == fig_cols:
            j = 0
            i += 1


def boxenplot(df, features, fig_cols, hue=False, palette='viridis', figsize=(16, 12)):
    """
    Phases:
         1. creation of figure according to argument specifications
         2. loop for boxplot plot by axis
         3. graphic formatting
         4. validation of surplus axes

     Arguments:
         df -- database for plotting [pandas.DataFrame]
         features -- set of columns to be evaluated [list]
         fig_cols -- matplotlib figure specifications [int]
         hue -- response variable contained in base [string - default: False]
         palette -- color palette [string / list - default: 'viridis']
         figsize -- plot figure dimensions [tuple - default: (16, 12)]

     Return:
         None
    """

    n_features = len(features)
    fig_rows = ceil(n_features / fig_cols)
    i, j, color_idx = (0, 0, 0)

    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=figsize)

    for col in features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]

        if hue != False:
            sns.boxenplot(x=df[hue], y=df[col], ax=ax, palette=palette)
        else:
            sns.boxenplot(y=df[col], ax=ax, palette=palette)

        format_spines(ax, right_border=False)
        ax.set_title(f'Feature: {col.upper()}', size=14, color='dimgrey')
        plt.tight_layout()

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        if n_plots >= n_features:
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        j += 1
        if j == fig_cols:
            j = 0
            i += 1


# Function responsible for plotting the volumetry of a categorical variable (breaking by hue is optional)
def countplot(df, feature, order=True, hue=False, label_names=None, palette='plasma', colors=['darkgray', 'navy'],
              figsize=(12, 5), loc_legend='lower left', width=0.75, sub_width=0.3, sub_size=12):
    """
Phases:
        1. customization of the plot according to the presence (or not) of the hue parameter
        2. definition of figures and plotting of appropriate graphics
        3. plot customization

    Arguments:
        df -- DataFrame target of analysis [pandas.DataFrame]
        feature -- column to parse [string]
        order -- boolean flag to indicate plot ordering [bool - default: True]
        hue -- parse break parameter [string - default: False]
        label_names -- description of labels to be placed in the legend [list - default: None]
        palette -- color palette to be used in the singular plot of the variable [string - default: 'viridis']
        colors -- colors to be used in plot broken by hue [list - default: ['darkgray', 'navy']]
        figsize -- plot dimensions [tuple - default: (15, 5)]
        loc_legend -- legend position in case of plot by hue [string - default: 'best']
        width -- width of bars when plotting by hue [float - default: 0.5]
        sub_width -- label alignment parameter in case of plotting by hue [float - default: 0.3]

    Return:
        None
    """

    ncount = len(df)
    if hue != False:
        # Redifinindo dimensões e plotando gráfico solo + versus variável categórica
        figsize = (figsize[0], figsize[1] * 2)
        fig, axs = plt.subplots(nrows=2, ncols=1, figsize=figsize)
        if order:
            sns.countplot(x=feature, data=df, palette=palette, ax=axs[0], order=df[feature].value_counts().index)
        else:
            sns.countplot(x=feature, data=df, palette=palette, ax=axs[0])

        feature_rate = pd.crosstab(df[feature], df[hue])
        percent_df = feature_rate.div(feature_rate.sum(1).astype(float), axis=0)
        if order:
            sort_cols = list(df[feature].value_counts().index)
            sorter_index = dict(zip(sort_cols, range(len(sort_cols))))
            percent_df['rank'] = percent_df.index.map(sorter_index)
            percent_df = percent_df.sort_values(by='rank')
            percent_df = percent_df.drop('rank', axis=1)
            percent_df.plot(kind='bar', stacked=True, ax=axs[1], color=colors, width=width)
        else:
            percent_df.plot(kind='bar', stacked=True, ax=axs[1], color=colors, width=width)
        # sns.countplot(x=feature, data=df, palette=colors, hue=hue, ax=axs[1], order=df[feature].value_counts().index)

        for p in axs[0].patches:
            x = p.get_bbox().get_points()[:, 0]
            y = p.get_bbox().get_points()[1, 1]
            axs[0].annotate('{:.1f}%'.format(100. * y / ncount), (x.mean(), y), ha='center', va='bottom',
                            size=sub_size)

        for p in axs[1].patches:
            # Coletando parâmetros
            height = p.get_height()
            width = p.get_width()
            x = p.get_x()
            y = p.get_y()

            label_text = f'{round(100 * height, 1)}%'
            label_x = x + width - sub_width
            label_y = y + height / 2
            axs[1].text(label_x, label_y, label_text, ha='center', va='center', color='white', fontweight='bold',
                        size=sub_size)

        axs[0].set_title(f'Análise de Volumetria da Variável {feature}', size=14, color='dimgrey', pad=20)
        axs[0].set_ylabel('Volumetria')
        axs[1].set_title(f'Análise de Volumetria da Variável {feature} por {hue}', size=14, color='dimgrey', pad=20)
        axs[1].set_ylabel('Percentual')

        for ax in axs:
            format_spines(ax, right_border=False)

        plt.legend(loc=loc_legend, title=f'{hue}', labels=label_names)

    else:
        fig, ax = plt.subplots(figsize=figsize)
        if order:
            sns.countplot(x=feature, data=df, palette=palette, ax=ax, order=df[feature].value_counts().index)
        else:
            sns.countplot(x=feature, data=df, palette=palette, ax=ax)

        ax.set_ylabel('Volumetria')
        format_spines(ax, right_border=False)

        for p in ax.patches:
            x = p.get_bbox().get_points()[:, 0]
            y = p.get_bbox().get_points()[1, 1]
            ax.annotate('{:.1f}%'.format(100. * y / ncount), (x.mean(), y), ha='center', va='bottom')

        ax.set_title(f'Análise de Volumetria da Variável {feature}', size=14, color='dimgrey')

    plt.tight_layout()
    plt.show()

# Function responsible for plotting single categorical variable volumetry in updated format
def single_countplot(df, ax, x=None, y=None, top=None, order=True, hue=False, palette='plasma',
                     width=0.75, sub_width=0.3, sub_size=12):
    """
    Parameters
     ----------
     classifiers: dictionary-shaped set of classifiers [dict]
     X: array with the data to be used in training [np.array]
     y: array with the target vector of the model [np.array]

     Return
     -------
     None
    """

    ncount = len(df)
    if x:
        col = x
    else:
        col = y

    if top is not None:
        cat_count = df[col].value_counts()
        top_categories = cat_count[:top].index
        df = df[df[col].isin(top_categories)]

    if hue != False:
        if order:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax, order=df[col].value_counts().index, hue=hue)
        else:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax, hue=hue)
    else:
        if order:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax, order=df[col].value_counts().index)
        else:
            sns.countplot(x=x, y=y, data=df, palette=palette, ax=ax)

    format_spines(ax, right_border=False)

    if x:
        for p in ax.patches:
            x = p.get_bbox().get_points()[:, 0]
            y = p.get_bbox().get_points()[1, 1]
            ax.annotate('{}\n{:.1f}%'.format(int(y), 100. * y / ncount), (x.mean(), y), ha='center', va='bottom')
    else:
        for p in ax.patches:
            x = p.get_bbox().get_points()[1, 0]
            y = p.get_bbox().get_points()[:, 1]
            ax.annotate('{} ({:.1f}%)'.format(int(x), 100. * x / ncount), (x, y.mean()), va='center')


# Function for plotting the volumetry of categorical variables in the dataset
def catplot_analysis(df_categorical, fig_cols=3, hue=False, palette='viridis', figsize=(16, 10)):
    """
    Phases:
         1. return of categorical variables from the dataset
         2. parameterization of plot variables
         3. applying repeat loops to plots / formatting

     Arguments:
         df -- dataset to parse [pandas.DataFrame]
         fig_cols -- number of columns of figure matplotlib [int]

     Return:
         None
    """

    if hue != False:
        cat_features = list(df_categorical.drop(hue, axis=1).columns)
    else:
        cat_features = list(df_categorical.columns)

    total_cols = len(cat_features)
    fig_cols = fig_cols
    fig_rows = ceil(total_cols / fig_cols)
    ncount = len(cat_features)

    sns.set(style='white', palette='muted', color_codes=True)
    total_cols = len(cat_features)
    fig_rows = ceil(total_cols / fig_cols)

    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=(figsize))
    i, j = 0, 0

    for col in cat_features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]
        if hue != False:
            sns.countplot(y=col, data=df_categorical, palette=palette, ax=ax, hue=hue,
                          order=df_categorical[col].value_counts().index)
        else:
            sns.countplot(y=col, data=df_categorical, palette=palette, ax=ax,
                          order=df_categorical[col].value_counts().index)

        format_spines(ax, right_border=False)
        AnnotateBars(n_dec=0, color='dimgrey').horizontal(ax)
        ax.set_title(col)

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        if n_plots >= len(cat_features):
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    plt.tight_layout()
    plt.show()


# Function for plotting the volumetry of categorical variables in the dataset
def numplot_analysis(df_numerical, fig_cols=3, color_sequence=['darkslateblue', 'mediumseagreen', 'darkslateblue'],
                     hue=False, color_hue=['darkslateblue', 'crimson'], hist=False):
    """
    Phases:
         1. return of categorical variables from the dataset
         2. parameterization of plot variables
         3. applying repeat loops to plots / formatting

     Arguments:
         df -- dataset to parse [pandas.DataFrame]
         fig_cols -- number of columns of figure matplotlib [int]

     Return:
         None
    """

    sns.set(style='white', palette='muted', color_codes=True)

    #num_features = [col for col, dtype in df.dtypes.items() if dtype != 'object']
    #df_numerical = df.loc[:, num_features]

    if hue != False:
        num_features = list(df_numerical.drop(hue, axis=1).columns)
    else:
        num_features = list(df_numerical.columns)

    total_cols = len(num_features)
    fig_cols = fig_cols
    fig_rows = ceil(total_cols / fig_cols)

    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=(fig_cols * 5, fig_rows * 4.5))
    sns.despine(left=True)
    i, j = 0, 0

    color_idx = 0
    for col in num_features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]
        target_idx = 0

        if hue != False:
            for classe in df_numerical[hue].value_counts().index:
                df_hue = df_numerical[df_numerical[hue] == classe]
                sns.distplot(df_hue[col], color=color_hue[target_idx], hist=hist, ax=ax, label=classe)
                target_idx += 1
                ax.set_title(col)
        else:
            sns.distplot(df_numerical[col], color=color_sequence[color_idx], hist=hist, ax=ax)
            ax.set_title(col, color=color_sequence[color_idx])

        format_spines(ax, right_border=False)

        color_idx += 1
        j += 1
        if j == fig_cols:
            j = 0
            i += 1
            color_idx = 0

    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        if n_plots >= len(num_features):
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    plt.setp(axs, yticks=[])
    plt.tight_layout()
    plt.show()


# Function for plotting the representativeness of each category regarding a specific hue
def catplot_percentage_analysis(df_categorical, hue, fig_cols=2, palette='viridis', figsize=(16, 10)):
    """
    Phases:
         1. return of categorical variables from the dataset
         2. parameterization of plot variables
         3. applying repeat loops to plots / formatting

     Arguments:
         df -- dataset to parse [pandas.DataFrame]
         fig_cols -- number of columns of figure matplotlib [int]

     Return:
         None
    """
 
    sns.set(style='white', palette='muted', color_codes=True)
    cat_features = list(df_categorical.drop(hue, axis=1).columns)
    total_cols = len(cat_features)
    fig_rows = ceil(total_cols / fig_cols)

    fig, axs = plt.subplots(nrows=fig_rows, ncols=fig_cols, figsize=(figsize))
    i, j = 0, 0

    for col in cat_features:
        try:
            ax = axs[i, j]
        except:
            ax = axs[j]

        col_to_hue = pd.crosstab(df_categorical[col], df_categorical[hue])
        col_to_hue.div(col_to_hue.sum(1).astype(float), axis=0).plot(kind='barh', stacked=True, ax=ax,
                                                                     colors=palette)

        format_spines(ax, right_border=False)
        ax.set_title(col)
        ax.set_ylabel('')

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    i, j = (0, 0)
    for n_plots in range(fig_rows * fig_cols):

        if n_plots >= len(cat_features):
            try:
                axs[i][j].axis('off')
            except TypeError as e:
                axs[j].axis('off')

        j += 1
        if j == fig_cols:
            j = 0
            i += 1

    plt.tight_layout()
    plt.show()


def mean_sum_analysis(df, group_col, value_col, orient='vertical', palette='plasma', figsize=(15, 6)):
    """
    Parameters
     ----------
     classifiers: dictionary-shaped set of classifiers [dict]
     X: array with the data to be used in training [np.array]
     y: array with the target vector of the model [np.array]

     Return
     -------
     None
    """

    # Grouping data
    df_mean = df.groupby(group_col, as_index=False).mean()
    df_sum = df.groupby(group_col, as_index=False).sum()

    # Sorting grouped dataframes
    df_mean.sort_values(by=value_col, ascending=False, inplace=True)
    sorter = list(df_mean[group_col].values)
    sorter_idx = dict(zip(sorter, range(len(sorter))))
    df_sum['mean_rank'] = df_mean[group_col].map(sorter_idx)
    df_sum.sort_values(by='mean_rank', inplace=True)
    df_sum.drop('mean_rank', axis=1, inplace=True)

    # Plotting data
    fig, axs = plt.subplots(ncols=2, figsize=figsize)
    if orient == 'vertical':
        sns.barplot(x=value_col, y=group_col, data=df_mean, ax=axs[0], palette=palette)
        sns.barplot(x=value_col, y=group_col, data=df_sum, ax=axs[1], palette=palette)
        AnnotateBars(n_dec=0, font_size=12, color='black').horizontal(axs[0])
        AnnotateBars(n_dec=0, font_size=12, color='black').horizontal(axs[1])
    elif orient == 'horizontal':
        sns.barplot(x=group_col, y=value_col, data=df_mean, ax=axs[0], palette=palette)
        sns.barplot(x=group_col, y=value_col, data=df_sum, ax=axs[1], palette=palette)
        AnnotateBars(n_dec=0, font_size=12, color='black').vertical(axs[0])
        AnnotateBars(n_dec=0, font_size=12, color='black').vertical(axs[1])

    # Customizing plot
    for ax in axs:
        format_spines(ax, right_border=False)
        ax.set_ylabel('')
    axs[0].set_title(f'Mean of {value_col} by {group_col}', size=14, color='dimgrey')
    axs[1].set_title(f'Sum of {value_col} by {group_col}', size=14, color='dimgrey')

    plt.tight_layout()
    plt.show()


def answear_plot(grouped_data, grouped_col, list_cols, axs, top=5, bottom_filter=True, palette='plasma'):
    """
    Parameters
     ----------
     grouped_data: pandas DataFrame with data already grouped for analysis [pd.DataFrame]
     grouped_col: pivot column reference used in grouping [string]
     list_cols: list of columns to be used in the analysis [list]
     axs: axes to be used in the plot [matplotlib.axis]
     top: number of entries in head and tail analyzes [int, default: 5]
     bottom_filter: flag for filtering elements with at least 1 occurrence in the bot [bool, default: True]
     palette: color palette used in the plot [string, default: 'plasma']

     Return
     -------
     None
    """

    # Extracting plot dims and looking at number of cols
    nrows = axs.shape[0]
    ncols = axs.shape[1]
    if len(list_cols) != ncols:
        print(f'Number of cols passed in list_cols arg is different for figure cols axis. Please check it.')
        return None

    # Iterating over columns in the list and creating charts
    i, j = 0, 0
    for col in list_cols:
        ax0 = axs[-3, j]
        ax1 = axs[-2, j]
        ax2 = axs[-1, j]
        sorted_data = grouped_data.sort_values(by=col, ascending=False)

        # First Line: Top entries
        sns.barplot(x=col, y=grouped_col, data=sorted_data.head(top), ax=ax1, palette=palette)
        ax1.set_title(f'Top {top} {grouped_col.capitalize()} with Highest \n{col.capitalize()}')

        # Second Line: Bottom entries
        if bottom_filter:
            sns.barplot(x=col, y=grouped_col, data=sorted_data[sorted_data[col] > 0].tail(top), ax=ax2,
                        palette=palette+'_r')
        else:
            sns.barplot(x=col, y=grouped_col, data=sorted_data.tail(top), ax=ax2, palette=palette+'_r')
        ax2.set_title(f'Top {top} {grouped_col.capitalize()} with Lowest \n{col.capitalize()}')

        # Customizing charts
        for ax in ax1, ax2:
            ax.set_xlim(0, grouped_data[col].max())
            ax.set_ylabel('')
            format_spines(ax, right_border=False)

        # Annotations
        mean_ind = grouped_data[col].mean()
        ax0.text(0.50, 0.30, round(mean_ind, 2), fontsize=45, ha='center')
        ax0.text(0.50, 0.12, f'is the average of {col}', fontsize=12, ha='center')
        ax0.text(0.50, 0.00, f'by {grouped_col}', fontsize=12, ha='center')
        ax0.axis('off')

        j += 1

"""
--------------------------------------------
-------- 3. DATAFRAME ANALYSIS ---------
--------------------------------------------
"""


def data_overview(df, corr=False, label_name=None, sort_by='qtd_null', thresh_percent_null=0, thresh_corr_label=0):
    """
    Phases:
         1. survey of attributes with null data in the set
         2. Primitive type analysis of each attribute
         3. analysis of the number of entries in case of categorical attributes
         4. extraction of the Pearson correlation with the target for each attribute
         5. application of rules defined in arguments
         6. return of the created overview dataset

     Arguments:
         df -- DataFrame to parse [pandas.DataFrame]
         label_name -- variable name target [string]
         sort_by -- overview dataset sort column [string - default: 'qtd_null']
         thresh_percent_null -- null data filter [int - default: 0]
         threh_corr_label -- correlation filter with target [int - default: 0]

     Return
         df_overview -- consolidated dataet containing column analysis [pandas.DataFrame]
    """

    df_null = pd.DataFrame(df.isnull().sum()).reset_index()
    df_null.columns = ['feature', 'qtd_null']
    df_null['percent_null'] = df_null['qtd_null'] / len(df)

    df_null['dtype'] = df_null['feature'].apply(lambda x: df[x].dtype)
    df_null['qtd_cat'] = [len(df[col].value_counts()) if df[col].dtype == 'object' else 0 for col in
                          df_null['feature'].values]

    if corr:
        label_corr = pd.DataFrame(df.corr()[label_name])
        label_corr = label_corr.reset_index()
        label_corr.columns = ['feature', 'target_pearson_corr']

        df_null_overview = df_null.merge(label_corr, how='left', on='feature')
        df_null_overview.query('target_pearson_corr > @thresh_corr_label')
    else:
        df_null_overview = df_null

    df_null_overview.query('percent_null > @thresh_percent_null')

    df_null_overview = df_null_overview.sort_values(by=sort_by, ascending=False)
    df_null_overview = df_null_overview.reset_index(drop=True)

    return df_null_overview
