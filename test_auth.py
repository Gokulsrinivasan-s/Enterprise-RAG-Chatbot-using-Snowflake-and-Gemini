from auth import authenticate_user


user = authenticate_user(
    "admin",
    "admin123"
)


print(user)