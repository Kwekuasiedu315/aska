from collections import namedtuple


# Define a namedtuple to represent search results
SearchResult = namedtuple(
    "SearchResult", ["name", "location", "job_title", "profile_url"]
)

# Dummy data for testing
dummy_data = [
    SearchResult(
        name="John Smith",
        location="New York, NY",
        job_title="Software Engineer",
        profile_url="https://example.com/johnsmith",
    ),
    SearchResult(
        name="Jane Doe",
        location="San Francisco, CA",
        job_title="Product Manager",
        profile_url="https://example.com/janedoe",
    ),
    SearchResult(
        name="David Lee",
        location="Seattle, WA",
        job_title="Data Analyst",
        profile_url="https://example.com/davidlee",
    ),
    SearchResult(
        name="Amy Chen",
        location="Boston, MA",
        job_title="Marketing Specialist",
        profile_url="https://example.com/amychen",
    ),
    SearchResult(
        name="Mark Johnson",
        location="Chicago, IL",
        job_title="Sales Manager",
        profile_url="https://example.com/markjohnson",
    ),
    SearchResult(
        name="Karen Kim",
        location="Los Angeles, CA",
        job_title="Graphic Designer",
        profile_url="https://example.com/karenkim",
    ),
    SearchResult(
        name="Chris Taylor",
        location="Austin, TX",
        job_title="Software Developer",
        profile_url="https://example.com/christaylor",
    ),
    SearchResult(
        name="Julia Rodriguez",
        location="Miami, FL",
        job_title="Project Manager",
        profile_url="https://example.com/juliarodriguez",
    ),
    SearchResult(
        name="Michael Brown",
        location="Denver, CO",
        job_title="Business Analyst",
        profile_url="https://example.com/michaelbrown",
    ),
    SearchResult(
        name="Lisa Nguyen",
        location="Portland, OR",
        job_title="UX Designer",
        profile_url="https://example.com/lisanguyen",
    ),
]

posts = [
    {
        "id": 1,
        "author": {
            "id": 1,
            "full_name": "John Smith",
            "profile_picture": {"url": "https://via.placeholder.com/150"},
        },
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "image": "https://via.placeholder.com/500x250",
        "timestamp": "2023-04-01 10:00:00",
        "likes": 10,
        "comments": [
            {
                "id": 1,
                "author": {
                    "id": 2,
                    "full_name": "Jane Doe",
                    "profile_picture": {"url": "https://via.placeholder.com/150"},
                },
                "content": "Great post!",
                "timestamp": "2023-04-01 10:05:00",
            },
            {
                "id": 2,
                "author": {
                    "id": 3,
                    "full_name": "Bob Johnson",
                    "profile_picture": {
                        "url": "https://via.placeholder.com/150",
                    },
                },
                "replies": [
                    {
                        "id": 1,
                        "author": {
                            "id": 2,
                            "full_name": "Jane Doe",
                            "profile_picture": {
                                "url": "https://via.placeholder.com/150"
                            },
                        },
                        "content": "you like commenting too much",
                        "timestamp": "2 minutes ago",
                    }
                ],
                "content": "I love this!",
                "timestamp": "2023-04-01 10:10:00",
            },
        ],
    },
    {
        "id": 2,
        "author": {
            "id": 4,
            "full_name": "Emily Chen",
            "profile_picture": {"url": "https://via.placeholder.com/150"},
        },
        "content": "Check out my new recipe!",
        "timestamp": "2023-04-05 12:00:00",
        "likes": 5,
        "comments": [
            {
                "id": 3,
                "author": {
                    "id": 5,
                    "full_name": "David Lee",
                    "profile_picture": {"url": "https://via.placeholder.com/150"},
                },
                "replies": [
                    {
                        "id": 2,
                        "author": {
                            "id": 6,
                            "full_name": "Lisa Kim",
                            "profile_picture": {
                                "url": "https://via.placeholder.com/150"
                            },
                        },
                        "content": "Looks delicious, can't wait to try it!",
                        "timestamp": "1 hour ago",
                    }
                ],
                "content": "This looks amazing!",
                "timestamp": "2023-04-05 12:10:00",
            },
            {
                "id": 4,
                "author": {
                    "id": 7,
                    "full_name": "Michael Davis",
                    "profile_picture": {
                        "url": "https://via.placeholder.com/150",
                    },
                },
                "content": "I'm not a fan of this ingredient...",
                "timestamp": "2023-04-05 12:30:00",
            },
        ],
    },
    {
        "id": 1,
        "author": {
            "id": 1,
            "full_name": "John Smith",
            "profile_picture": {"url": "https://via.placeholder.com/150"},
        },
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "image": "https://via.placeholder.com/500x250",
        "timestamp": "2023-04-01 10:00:00",
        "likes": 10,
        "comments": [
            {
                "id": 1,
                "author": {
                    "id": 2,
                    "full_name": "Jane Doe",
                    "profile_picture": {"url": "https://via.placeholder.com/150"},
                },
                "content": "Great post!",
                "timestamp": "2023-04-01 10:05:00",
            },
            {
                "id": 2,
                "author": {
                    "id": 3,
                    "full_name": "Bob Johnson",
                    "profile_picture": {
                        "url": "https://via.placeholder.com/150",
                    },
                },
                "replies": [
                    {
                        "id": 1,
                        "author": {
                            "id": 2,
                            "full_name": "Jane Doe",
                            "profile_picture": {
                                "url": "https://via.placeholder.com/150"
                            },
                        },
                        "content": "you like commenting too much",
                        "timestamp": "2 minutes ago",
                    }
                ],
                "content": "I love this!",
                "timestamp": "2023-04-01 10:10:00",
            },
        ],
    },
]

user = {
    "id": 2,
    "first_name": "Adwoa",
    "middle_name": "Yaa",
    "last_name": "Appiah",
    "nickname": "Adyaa",
    "full_name": "Adwoa Yaa Appiah",
    "email": "adwoa.appiah@gmail.com",
    "phone_number": "0241234567",
    "birthdate": "1995-06-15",
    "gender": "F",
    "bio": "Software developer",
    "friendship_status": None,
    "profile_picture": "http://127.0.0.1:8000/media/users/IMG_20210920_100458_312.jpg",
    "cover_picture": "http://127.0.0.1:8000/media/users/IMG_20210920_100458_312.jpg",
    "school": "University of Ghana",
    "education_history": ["St. Monica's Senior High School"],
    "subjects": ["Computer Science", "Mathematics"],
    "level": "Undergraduate",
    "points": 200,
    "url": "http://127.0.0.1:8000/api/users/2/",
    "date_joined": "2023-03-25T09:13:36.104947Z",
    "is_active": True,
    "last_login": "2023-03-27T06:56:39.442993Z",
}

friends = [
    {
        "friend": {
            "username": "johndoe",
            "email": "johndoe@example.com",
            "profile_picture": "/media/profile_pictures/johndoe.jpg",
        }
    },
    {
        "friend": {
            "username": "janedoe",
            "email": "janedoe@example.com",
            "profile_picture": "/media/profile_pictures/janedoe.jpg",
        }
    },
    {
        "friend": {
            "username": "bobsmith",
            "email": "bobsmith@example.com",
            "profile_picture": "/media/profile_pictures/bobsmith.jpg",
        }
    },
    {
        "friend": {
            "username": "kwame",
            "email": "kwame@example.com",
            "profile_picture": "/media/profile_pictures/kwame.jpg",
            "status": "online",
        }
    },
    {
        "friend": {
            "username": "ama",
            "email": "ama@example.com",
            "profile_picture": "/media/profile_pictures/ama.jpg",
            "status": "offline",
        }
    },
    {
        "friend": {
            "username": "yaw",
            "email": "yaw@example.com",
            "profile_picture": "/media/profile_pictures/yaw.jpg",
            "status": "online",
        }
    },
    {
        "friend": {
            "username": "akosua",
            "email": "akosua@example.com",
            "profile_picture": "/media/profile_pictures/akosua.jpg",
            "status": "offline",
        }
    },
]


album = {
    "user_photos": [
        {
            "name": "Photo 1",
            "url": "https://dummyimage.com/600x400/000/fff&text=Photo+1",
        },
        {
            "name": "Photo 2",
            "url": "https://dummyimage.com/600x400/000/fff&text=Photo+2",
        },
        {
            "name": "Photo 3",
            "url": "https://dummyimage.com/600x400/000/fff&text=Photo+3",
        },
    ],
    "user_videos": [
        {
            "name": "Video 1",
            "url": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
            "mime_type": "video/mp4",
        },
        {
            "name": "Video 2",
            "url": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_2mb.mp4",
            "mime_type": "video/mp4",
        },
        {
            "name": "Video 3",
            "url": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_5mb.mp4",
            "mime_type": "video/mp4",
        },
    ],
}
