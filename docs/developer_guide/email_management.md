# How to write html files for emails?

For an example of email style and structure, please refer to api_volontaria/apps/volunteer/templates/participation_confirmation_email.html.

* Copy-paste css classes from the style section in the email head. (Ideally, we would extend a base.html file, but using SendinBlue limits the ability to test css from a separate file. So we have to accept some level of redundancy.)
* Make sure you include the email footer at the end of your html file.
