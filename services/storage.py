def get(page, key, default=None):
    return page.client_storage.get(key) or default

def set(page, key, value):
    page.client_storage.set(key, value)
