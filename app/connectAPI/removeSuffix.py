def clean_api_response(response: str) -> str:
    # Remove the unwanted part from the end of the string
    unwanted_suffix = ' ", "error_code": 0}'
    if response.endswith(unwanted_suffix):
        cleaned_response = response[:-len(unwanted_suffix)]
        # Remove any trailing quotation mark if present
        cleaned_response = cleaned_response.rstrip('"')
        return cleaned_response
    else:
        return response