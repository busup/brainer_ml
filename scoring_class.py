#
# Copyright (c) 2023-2024 by Dribia Data Research.
# This file is part of project Brainer,
# and is released under the MIT License Agreement.
# See the LICENSE file for more information.
#
"""**Linear score**.

This class is used to compute global and categorical (tag) linear
scores given some features and its respective weights.
"""

import numpy as np
import pandas as pd

from brainer.core.exceptions import ZeroWeightsError
from brainer.core.logger import logger


class LinearScore:
    """Class for linear score operations.

    It has methods to compute global and categorical (tag) linear
    scores, as well as to store in the Data Base.
    """

    def __init__(
        self,
        *,
        df_weights: pd.DataFrame,
        df_features: pd.DataFrame,
        primarey_key: str,
    ):
        """Initialize the linear scorer.

        Args:
            df_weights: Dataframe with the features weights.
            df_features: Dataframe with the features.
            primarey_key: Primary key of the features dataframe.
        """
        self.df_weights = df_weights
        self.df_features = df_features
        self.primary_key = primarey_key

    def calculate_score(self) -> pd.DataFrame:
        """Calculates global and categorical (tag) linear scores.

        Returns:
            scores: dataframe with global and categorical (tag) scores.

        """
        logger.debug("Start calculating linear scores.")

        # check if there are nonzero WEIGHTS
        if np.isclose(self.df_weights["weight"].sum(), 0):
            logger.error("The weight vector cannot be all zeroes.")
            raise ZeroWeightsError("The weight vector cannot have all elements zero.")

        # apply linear formula with scaling for global scores
        scores = pd.DataFrame(
            data=self.df_features[self.primary_key], columns=[self.primary_key]
        )

        scores = scores.assign(score_global=self._score_calculator(tag=None))

        # apply linear formula with scaling for scores in each TAG
        for tag in self.df_weights["tag"].unique():
            scores[f"score_{tag}"] = self._score_calculator(tag=tag)

        logger.debug("Finish calculating linear scores.")

        return scores

    def _score_calculator(self, tag: str | None) -> pd.Series:
        """Calculates the score.

        Args:
            tag: Tag to filter the weights and features.

        Returns:
            scores: Series with the scores.

        """
        if (tag is not None) and (tag not in self.df_weights.tag.unique()):
            raise ValueError(f"Tag `{tag}` not found in weights.")

        features_cols = self.df_weights["feature"].to_list()
        # fill missing features values with 0
        features_df = self.df_features[features_cols].copy()
        features_df = features_df.fillna(0)

        # Use the name of the features (feature) as index in _weights.
        # Columns in features_df have also the same name.
        # This guarantees the correct dot product.
        weights_df = self.df_weights.set_index("feature")

        if tag:
            logger.debug(f"Calculating {tag} linear scores.")
            tag_features_cols = self.df_weights.loc[
                self.df_weights["tag"] == tag, "feature"
            ].to_list()
            _features_df = features_df[tag_features_cols]
            _weights_ser = weights_df.loc[weights_df["tag"] == tag, "weight"]
        else:
            logger.debug("Calculating global linear scores.")
            _features_df = features_df.copy()
            _weights_ser = weights_df["weight"]

        _norm = _weights_ser.sum()
        return _features_df.dot(_weights_ser) / _norm
