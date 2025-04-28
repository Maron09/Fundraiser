from django.contrib.auth.models import BaseUserManager




class UserManager(BaseUserManager):
    """"
    Custom user manager for User model.
    """
    def create_user(self, email, first_name, last_name, password=None):
        """"
        Creates and returns a user with an email, first name, last name and password.
        """
        if not email:
            raise ValueError("user must have an email address")
        if not first_name:
            raise ValueError("user must have a first name")
        if not last_name:
            raise ValueError("user must have a last name")
        
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password=None):
        """"
        Creates and returns a superuser with an email, first name, last name and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user