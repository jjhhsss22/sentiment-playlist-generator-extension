"""
Define potential errors for the AI prediction pipeline.
Just names,as these are for logging
"""

class PredictionError(Exception):
    pass

class EmotionMappingError(Exception):
    pass

class CoordinateError(Exception):
    pass

class ProbabilityError(Exception):
    pass