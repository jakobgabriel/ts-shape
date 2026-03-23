import logging
import time
import inspect
import pandas as pd  # type: ignore
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """Generic pipeline builder for chaining any ts-shape class methods.

    Supports both @classmethod transforms (DataFrame in → DataFrame out) and
    instance-based classes (DataHarmonizer, CrossSignalAnalytics, CycleExtractor).

    Example — using any library class::

        from ts_shape.transform.filter.numeric_filter import DoubleFilter
        from ts_shape.transform.filter.datetime_filter import DateTimeFilter
        from ts_shape.transform.harmonization import DataHarmonizer
        from ts_shape.features.segment_analysis.segment_extractor import SegmentExtractor
        from ts_shape.features.segment_analysis.segment_processor import SegmentProcessor
        from ts_shape.features.segment_analysis.time_windowed_features import TimeWindowedFeatureTable

        result = (
            FeaturePipeline(df)
            .add_step(DateTimeFilter.filter_between_dates,
                      start_date='2024-01-01', end_date='2024-01-31')
            .add_step(DoubleFilter.filter_nan_value_double)
            .add_instance_step(DataHarmonizer,
                               call='resample_to_uniform', freq='1s')
            .add_step(SegmentExtractor.extract_time_ranges,
                      segment_uuid='order_number')
            .add_step(SegmentProcessor.apply_ranges,
                      time_ranges='$prev')
            .add_step(TimeWindowedFeatureTable.compute, freq='1min')
            .run()
        )

    The special value ``'$prev'`` can be used as a keyword argument value to
    reference the output of the previous step.  This is useful when a step
    needs a secondary DataFrame (e.g. ``apply_ranges`` needs ``time_ranges``).

    For instance-based classes, use ``add_instance_step`` which instantiates
    the class with the current DataFrame and calls the specified method.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        time_column: str = 'systime',
        uuid_column: str = 'uuid',
        value_column: str = 'value_double',
    ) -> None:
        """Initialize the pipeline with input data.

        Args:
            dataframe: Input DataFrame to process.
            time_column: Name of the timestamp column.
            uuid_column: Name of the UUID/signal identifier column.
            value_column: Name of the numeric value column.
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame.")
        self._dataframe = dataframe.copy()
        self._time_column = time_column
        self._uuid_column = uuid_column
        self._value_column = value_column
        self._steps: List[Tuple[str, str, Any]] = []

    def add_step(
        self,
        method: Callable[..., pd.DataFrame],
        **kwargs: Any,
    ) -> 'FeaturePipeline':
        """Add a @classmethod step that takes a DataFrame and returns a DataFrame.

        The current DataFrame is passed as the first positional argument
        (after ``cls``) automatically.

        Args:
            method: A classmethod reference, e.g. ``DoubleFilter.filter_nan_value_double``.
            **kwargs: Additional keyword arguments forwarded to the method.

        Returns:
            self, for chaining.
        """
        name = _method_label(method)
        self._steps.append(('classmethod', name, (method, kwargs)))
        return self

    def add_instance_step(
        self,
        cls: Type,
        call: str,
        init_kwargs: Optional[Dict[str, Any]] = None,
        **method_kwargs: Any,
    ) -> 'FeaturePipeline':
        """Add an instance-based step (e.g. DataHarmonizer, CrossSignalAnalytics).

        The class is instantiated with the current DataFrame plus the
        constructor's column-name parameters (``time_column``, ``uuid_column``,
        ``value_column``) when available.  Then ``call`` is invoked on the
        instance.

        Args:
            cls: The class to instantiate, e.g. ``DataHarmonizer``.
            call: Name of the instance method to call, e.g. ``'resample_to_uniform'``.
            init_kwargs: Extra keyword arguments for the constructor beyond
                the DataFrame and column names.
            **method_kwargs: Keyword arguments forwarded to the instance method.

        Returns:
            self, for chaining.
        """
        name = f"{cls.__name__}.{call}"
        self._steps.append((
            'instance',
            name,
            (cls, call, init_kwargs or {}, method_kwargs),
        ))
        return self

    def add_lambda_step(
        self,
        func: Callable[[pd.DataFrame], pd.DataFrame],
        name: Optional[str] = None,
    ) -> 'FeaturePipeline':
        """Add a custom callable step.

        Args:
            func: A function that takes a DataFrame and returns a DataFrame.
            name: Optional label for logging. Defaults to the function name.

        Returns:
            self, for chaining.
        """
        label = name or getattr(func, '__name__', 'lambda')
        self._steps.append(('lambda', label, func))
        return self

    @property
    def steps(self) -> List[str]:
        """Return the list of registered step names."""
        return [name for _, name, _ in self._steps]

    def run(self) -> pd.DataFrame:
        """Execute all steps sequentially and return the final DataFrame."""
        results = self._execute(capture_intermediates=False)
        return results

    def run_steps(self) -> Dict[str, pd.DataFrame]:
        """Execute all steps and return intermediate results keyed by step name.

        Useful for debugging.  The key ``'input'`` holds the original
        DataFrame; subsequent keys are the step names.
        """
        return self._execute(capture_intermediates=True)

    # ------------------------------------------------------------------
    # Internal execution
    # ------------------------------------------------------------------

    def _execute(self, capture_intermediates: bool) -> Any:
        if not self._steps:
            logger.warning("No steps registered. Returning input DataFrame.")
            if capture_intermediates:
                return {'input': self._dataframe.copy()}
            return self._dataframe.copy()

        df = self._dataframe.copy()
        intermediates: Dict[str, pd.DataFrame] = {}
        if capture_intermediates:
            intermediates['input'] = df.copy()

        prev_result: Optional[pd.DataFrame] = None
        total_start = time.time()

        for i, (step_type, name, payload) in enumerate(self._steps):
            step_start = time.time()
            logger.info(f"Step {i + 1}/{len(self._steps)}: {name}")

            if step_type == 'classmethod':
                method, kwargs = payload
                resolved = _resolve_kwargs(kwargs, prev_result)
                # Detect if the first positional parameter name is
                # explicitly provided in kwargs (e.g. dataframe=...).
                # In that case, don't auto-inject the pipeline df.
                first_param = _first_param_name(method)
                if first_param and first_param in resolved:
                    df = method(**resolved)
                else:
                    df = method(df, **resolved)

            elif step_type == 'instance':
                cls, call, init_kwargs, method_kwargs = payload
                resolved = _resolve_kwargs(method_kwargs, prev_result)
                instance = _build_instance(
                    cls, df,
                    time_column=self._time_column,
                    uuid_column=self._uuid_column,
                    value_column=self._value_column,
                    extra_kwargs=init_kwargs,
                )
                result = getattr(instance, call)(**resolved)
                if isinstance(result, pd.DataFrame):
                    df = result
                else:
                    logger.warning(
                        f"Step '{name}' returned {type(result).__name__} "
                        f"instead of DataFrame. Pipeline continues with "
                        f"previous DataFrame."
                    )

            elif step_type == 'lambda':
                df = payload(df)

            prev_result = df
            elapsed = time.time() - step_start
            logger.info(
                f"  → {name}: {len(df)} rows, "
                f"{len(df.columns)} cols ({elapsed:.3f}s)"
            )

            if capture_intermediates:
                intermediates[name] = df.copy()

        total_elapsed = time.time() - total_start
        logger.info(
            f"Pipeline complete: {len(self._steps)} steps in {total_elapsed:.3f}s. "
            f"Final shape: {df.shape}"
        )

        if capture_intermediates:
            return intermediates
        return df


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _first_param_name(method: Any) -> Optional[str]:
    """Return the name of the first non-cls/self parameter of a method."""
    try:
        sig = inspect.signature(method)
    except (ValueError, TypeError):
        return None
    for p in sig.parameters.values():
        if p.name in ('cls', 'self'):
            continue
        return p.name
    return None


def _method_label(method: Any) -> str:
    """Build a human-readable label for a method."""
    cls_name = ''
    if hasattr(method, '__self__'):
        cls_name = method.__self__.__name__ + '.'
    elif hasattr(method, '__qualname__'):
        parts = method.__qualname__.split('.')
        if len(parts) >= 2:
            cls_name = parts[-2] + '.'
    return f"{cls_name}{method.__name__}"


def _resolve_kwargs(
    kwargs: Dict[str, Any],
    prev_result: Optional[pd.DataFrame],
) -> Dict[str, Any]:
    """Replace ``'$prev'`` sentinel values with the previous step's result."""
    resolved = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and value == '$prev':
            if prev_result is None:
                raise ValueError(
                    f"Keyword argument '{key}' references '$prev' but there "
                    f"is no previous step result."
                )
            resolved[key] = prev_result
        else:
            resolved[key] = value
    return resolved


def _build_instance(
    cls: Type,
    dataframe: pd.DataFrame,
    time_column: str,
    uuid_column: str,
    value_column: str,
    extra_kwargs: Dict[str, Any],
) -> Any:
    """Instantiate an instance-based class, passing column names it accepts."""
    sig = inspect.signature(cls.__init__)
    params = set(sig.parameters.keys()) - {'self'}

    init_kwargs: Dict[str, Any] = {}

    # The first positional param (after self) is always the dataframe
    positional = [
        p for p in sig.parameters.values()
        if p.name != 'self'
        and p.default is inspect.Parameter.empty
        and p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]
    if positional:
        init_kwargs[positional[0].name] = dataframe

    # Pass column-name params the constructor accepts
    col_mapping = {
        'time_column': time_column,
        'uuid_column': uuid_column,
        'value_column': value_column,
        'column_name': time_column,
    }
    for param_name, value in col_mapping.items():
        if param_name in params and param_name not in extra_kwargs:
            init_kwargs[param_name] = value

    init_kwargs.update(extra_kwargs)
    return cls(**init_kwargs)
