import json
from filter import Filter

# Initialize global variable as a dictionary
all_filters = {}


def is_unique_name(name, channel_id):
    global all_filters
    if channel_id in all_filters:
        return all(f.name != name for f in all_filters[channel_id])
    return True


def load_filters_from_file():
    global all_filters
    try:
        with open("filters.json", "r") as f:
            all_filters = json.load(f)
            for channel_id, filters_json in all_filters.items():
                all_filters[channel_id] = [
                    Filter.from_json(f_json) for f_json in filters_json
                ]
    except FileNotFoundError:
        all_filters = {}


def save_filters_to_file():
    global all_filters
    with open("filters.json", "w") as f:
        saved_filters = {}
        for channel_id, filters in all_filters.items():
            saved_filters[channel_id] = [f.to_json() for f in filters]
        json.dump(saved_filters, f, indent=4)


# Example of modifying filters and saving changes
def add_new_filter(new_filter, channel_id):
    global all_filters
    str_channel_id = str(channel_id)
    if is_unique_name(new_filter.name, str_channel_id):
        if str_channel_id not in all_filters:
            all_filters[str_channel_id] = []
        all_filters[str_channel_id].append(new_filter)
        save_filters_to_file()
        return True  # Successfully added
    else:
        return False  # Name was not unique, did not add


def remove_filter(filter_name, channel_id):
    global all_filters
    str_channel_id = str(channel_id)
    if str_channel_id in all_filters:
        filter_to_remove = next(
            (f for f in all_filters[str_channel_id] if f.name == filter_name), None
        )
        if filter_to_remove:
            all_filters[str_channel_id].remove(filter_to_remove)
            save_filters_to_file()


def get_filters_by_chat_id(chat_id):
    global all_filters
    return all_filters.get(str(chat_id), [])
