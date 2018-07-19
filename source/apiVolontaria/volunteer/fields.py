from rest_framework.compat import unicode_to_repr


class CustomOrCurrentUserIdDefault(object):
    def set_context(self, serializer_field):

        self.user_id = None
        # Get the received user id if it exist in request data
        user_id = serializer_field.context['request'].data.get('user', None)

        if user_id:
            self.user_id = user_id

        if not self.user_id:
            # Set the user to currently logged user
            self.user_id = serializer_field.context['request'].user.id

    def __call__(self):
        return self.user_id

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)
