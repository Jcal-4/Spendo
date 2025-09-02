from ..models import CustomUser
from ..serializer import CustomUserSerializer


def get_users_by_email(email=None):
    if email:
        users = CustomUser.objects.filter(email=email)
    else:
        users = CustomUser.objects.all()
    return CustomUserSerializer(users, many=True).data


def get_user_by_username(username):
    try:
        user = CustomUser.objects.get(username=username)
        return CustomUserSerializer(user, many=False).data
    except CustomUser.DoesNotExist:
        return None
    
def create_user(username, email, password, first_name, last_name):
    #  Check for username and email if it exists. if it does then send back that error
    
    # if no duplicate found then continue with creation
    try: 
        customer_user = CustomUser.objects.create(
            username=username, email=email, first_name=first_name, last_name=last_name
        )
        customer_user.set_password(password)
        customer_user.save()
        return customer_user
    except Exception as e:
        return "Error occurred: " + str(e)  