# error_counters.py

class ErrorCounters:
    """
    Class to keep track of various error and condition counters.
    """

    def __init__(self):
        self.null_counter = 0
        self.skip_by_time_counter = 0
        self.try_except_counter = 0
        self.key_error_counter = 0
        self.condition_error_counter = 0  # For condition-related errors

    def report(self):
        print(f"INFO: Null data rows: {self.null_counter}")
        print(f"INFO: Skipped rows by time: {self.skip_by_time_counter}")
        print(f"INFO: Errors in implied volatility calculation: {self.try_except_counter}")
        print(f"INFO: KeyErrors encountered: {self.key_error_counter}")
        print(f"INFO: Condition-related errors: {self.condition_error_counter}")
