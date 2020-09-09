def input_convert(prompt, converter, reprompt,
                  break_string='', verify_func=None):
    input_ = input(prompt)

    while True:
        if input_ == break_string:
            return False

        try:
            input_ = converter(input_)
        except:
            input_ = input(reprompt)
        else:
            if verify_func is None:
                return input_
            elif verify_func(input_):
                return input_
            else:
                input_ = input(reprompt)


def get_param(default, *args, **kwargs):
    input_ = input_convert(*args, **kwargs)
    return input_ if input_ is not False else default
