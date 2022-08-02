import uuid
import json


def generate_uuid():
    i = str(uuid.uuid4())
    i = i.replace("-", "")
    return i


def generate_attributes_and_visibility():

    attribute_keys = [generate_uuid() for i in range(10)]

    attributes = {
        attribute_keys[0]: {"token": attribute_keys[0], "name": "car", "description": "sedan/SUV"},
        attribute_keys[1]: {"token": attribute_keys[1], "name": "truck", "description": "semi truck/box truck"},
        attribute_keys[2]: {"token": attribute_keys[2], "name": "van", "description": "van-shaped cargo vehicle"},
        attribute_keys[3]: {"token": attribute_keys[3], "name": "bus", "description": "city bus/coach bus"},
        attribute_keys[4]: {"token": attribute_keys[4], "name": "pedestrian", "description": "human"},
        attribute_keys[5]: {"token": attribute_keys[5], "name": "cyclist", "description": "bicycle"},
        attribute_keys[6]: {"token": attribute_keys[6], "name": "tricyclist", "description": "3-wheeled cycle"},
        attribute_keys[7]: {"token": attribute_keys[7], "name": "motorcyclist", "description": "motorcycle"},
        attribute_keys[8]: {"token": attribute_keys[8], "name": "barrowlist", "description": "human with a wheeled cart"},
        attribute_keys[9]: {"token": attribute_keys[9], "name": "trafficcone", "description": "cone on the road"},
    }

    visibility_keys = [generate_uuid() for i in range(9)]

    visibility = {
        visibility_keys[0]: {"token": visibility_keys[0], "level": "truncated_state: 0, occluded_state: 0",
                             "description": "non-truncated and fully visible"},
        visibility_keys[1]: {"token": visibility_keys[1], "level": "truncated_state: 0, occluded_state: 1",
                             "description": "non-truncated and partially occluded"},
        visibility_keys[2]: {"token": visibility_keys[2], "level": "truncated state: 0, occluded_state: 2",
                             "description": "non-truncated and largely occluded"},
        visibility_keys[3]: {"token": visibility_keys[3], "level": "truncated_state: 1, occluded_state: 0",
                             "description": "transversely-truncated and fully visible"},
        visibility_keys[4]: {"token": visibility_keys[4], "level": "truncated_state: 1, occluded_state: 1",
                             "description": "transversely-truncated and partially occluded"},
        visibility_keys[5]: {"token": visibility_keys[5], "level": "truncated state: 1, occluded_state: 2",
                             "description": "transversely-truncated and largely occluded"},
        visibility_keys[6]: {"token": visibility_keys[6], "level": "truncated_state: 2, occluded_state: 0",
                             "description": " longitudinally-truncated and fully visible"},
        visibility_keys[7]: {"token": visibility_keys[7], "level": "truncated_state: 2, occluded_state: 1",
                             "description": "longitudinally-truncated and partially occluded"},
        visibility_keys[8]: {"token": visibility_keys[8], "level": "truncated state: 2, occluded_state: 2",
                             "description": "longitudinally-truncated and largely occluded"},
    }

    with open("attributes.json", "w") as out_attr:
        json.dump(attributes, out_attr)

    with open("visibility.json", "w") as visi:
        json.dump(visibility, visi)

    print("attributes: ", attribute_keys)
    print("visibilities: ", visibility_keys)


if __name__ == "__main__":
    generate_attributes_and_visibility()