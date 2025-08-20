#  RimMirK's Telegram Bot Template - Template for building Telegram bots
#  Copyright (C) 2025-present RimMirK
#
#  This file is part of the RimMirK's Telegram Bot Template.
#
#  Telegram Bot Template is free software: you can use, modify, and redistribute
#  it under the terms of the Apache License 2.0.
#
#  Use responsibly and respect the author's work.
#
#  LICENSE: See LICENSE file for full terms.
#  NOTICE: Dear developer — this file is written especially for you.
#          Take a moment to read it: inside is a message, acknowledgements,
#          and guidance that matter.
#
#  Repository: https://github.com/RimMirK/RimMirKs_TelegramBotTemplate
#  Telegram: @RimMirK




import datetime
import pytz

def show_pretty_json(data, _print=True, _return=True, **kwargs):
    import json
    output = json.dumps(data, indent=4, ensure_ascii=False, **kwargs)
    
    if _print:
        print(output)
        
    if _return:
        return output
    

def to_json(data, indent=4, **kwargs):
    import json
    return json.dumps(data, indent=indent, ensure_ascii=False, **kwargs)

def format_date(timestamp: float, for_zero: str = "", add_utc=True) -> str:
    if timestamp == 0:
        return for_zero
    return datetime.datetime.fromtimestamp(timestamp, pytz.UTC).strftime('%d.%m.%Y %H:%M') \
            + (" (UTC)" if add_utc else "")


def pasters(text: str, ext: str = '', allow_206: bool = False) -> str:
    """
    Upload some text or code to the [paste.rs](https://paste.rs/)
    
    Args:
        text (str): a text or a code to upload.
        ext (str): a file extension. If pass `md`, `mdown`, or `markdown`, the paste is rendered as
          markdown into HTML. If ext is a known code file extension, the paste
          is syntax highlighted and returned as HTML. If ext is a known format
          extension, the paste is returned with the format's corresponding
          Content-Type. Otherwise, the paste is returned as unmodified text.
        allow_206 (bool): Should the response code 206 be allowed?
          If the response code is 201 (CREATED), then the entire paste was
          uploaded. If the response is 206 (PARTIAL), then the paste exceeded
          the server's maximum upload size, and only part of the paste was
          uploaded. If the response code is anything else, an error has
          occurred. Pasting is heavily rate limited.
    
    Returns:
        str: a link to the paste.
    
    Exceptions:
        requests.exceptions.HTTPError: 

    """
    import requests
    
    r = requests.post('https://paste.rs/', data=text)
        
    allowed_statuses = [201]
    if allow_206:
        allowed_statuses.append(206)
    if r.status_code not in allowed_statuses:
        raise requests.exceptions.HTTPError(f"Unexpected status {r.status_code}: {r.text}")
    
    return r.text + (f".{ext.removeprefix('.')}" if ext else '')

paste = pasters # default paster is paste.rs