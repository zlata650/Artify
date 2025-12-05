def filter_links_by_substring(links, substring):
    """
    Filters a list of links, returning only those that contain a given substring.

    Args:
        links (list[str]): List of URLs as strings.
        substring (str): The substring to filter by.

    Returns:
        list[str]: A filtered list of URLs.
    """
    return [link for link in links if substring in link]


def filter_links_by_multiple_substrings(links, substrings):
    """
    Filters a list of links, returning only those that contain any of the given substrings.

    Args:
        links (list[str]): List of URLs as strings.
        substrings (list[str]): List of substrings to filter by.

    Returns:
        list[str]: A filtered list of URLs.
    """
    return [link for link in links if any(substring in link for substring in substrings)]


def filter_links_by_domain(links, domain):
    """
    Filters a list of links, returning only those from a specific domain.

    Args:
        links (list[str]): List of URLs as strings.
        domain (str): The domain to filter by (e.g., 'example.com').

    Returns:
        list[str]: A filtered list of URLs from the specified domain.
    """
    return [link for link in links if domain in link]
