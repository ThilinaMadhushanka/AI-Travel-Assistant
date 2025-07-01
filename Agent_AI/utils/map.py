def generate_google_maps_link(origin: str, destination: str) -> str:
    """
    Generates a Google Maps direction link from origin to destination.

    Args:
        origin (str): Starting location (e.g., "Colombo, Sri Lanka").
        destination (str): Destination location (e.g., "Kandy, Sri Lanka").

    Returns:
        str: A URL that opens Google Maps with directions from origin to destination.
    """
    base_url = "https://www.google.com/maps/dir/?api=1"
    origin_param = f"origin={origin.replace(' ', '+')}"
    destination_param = f"destination={destination.replace(' ', '+')}"
    return f"{base_url}&{origin_param}&{destination_param}"
