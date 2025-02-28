def get_file_extension(track,lang):
    ext = {

        'sql': '.sql',
        'mysql': '.sql'
    }
    return ext[lang] or ext[track]
