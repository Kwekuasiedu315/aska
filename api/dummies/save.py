import json
from api.models import CustomUser

# Load the dummy data from a file
with open("users.json", "r") as f:
    users = json.load(f)

# Iterate over the data and create CustomUser instances
def dummy_user():
    for user in users:
        user = CustomUser(
            first_name=user["first_name"],
            last_name=user["last_name"],
            middle_name=user.get("middle_name"),
            phone_number=user["phone_number"],
            gender=user["gender"],
            birthdate=user["birthdate"],
            level=user["level"],
        )
        user.save()
