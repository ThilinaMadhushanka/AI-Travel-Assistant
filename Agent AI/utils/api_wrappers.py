def generate_google_maps_link(origin, destination):
    base = "https://www.google.com/maps/dir/?api=1"
    return f"{base}&origin={origin}&destination={destination}"