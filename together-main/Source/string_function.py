def check_keywords_in_string(input_string, keywords):
    for keyword in keywords:
        if keyword in input_string:
            return True
    return False