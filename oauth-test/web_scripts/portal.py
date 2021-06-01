#from ..user import User
from flask_login import LoginManager, current_user

def portal():
    return f"""
     <h1>Home</h1>
     <h2>Welcome {current_user.name}, to the portal</h2>
     <h3>You are logged in</h3>
     <p>{current_user.email}</p>
     <p>{current_user.id}</p><br>
     <p>
         <a class="button" href="/settings"    >Settings</a><br>
         <a class="button" href="/ddns"        >DDNS</a><br>
     </p>
     <a class="button" href="/logout"      >Logout</a><br>

    """
    # f"""
    #         User information: <br>
    #         Name: {user_info["name"]} <br>
    #         Email: {user_info["email"]} <br>
    #         Avatar <img src="{user_info.get('avatar_url')}"> <br>
    #         <a href="/">Home</a>
    #         """
    # "<p>Hello, {}! You're logged in! Email: {}</p>"
    # "<div><p>Google Profile Picture:</p>"
    # '<img src="{}" alt="Google profile pic"></img></div>'
    # '<a class="button" href="/logout">Logout</a>'.format(
    #     current_user.name, current_user.email, current_user.profile_pic
