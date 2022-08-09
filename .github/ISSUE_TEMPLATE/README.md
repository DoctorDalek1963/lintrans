# Using Google Forms to create anonymous GitHub issues

I wanted to use Google Forms to allow users to [submit a bug
report](https://forms.gle/Q82cLTtgPLcV4xQD6) or [suggest a new
feature](https://forms.gle/mVWbHiMBw9Zq5Ze37) without needing to create a GitHub account first.

I was following [this old
tutorial](http://ez34.net/2016/12/publish-anonymous-issues-on-github.html) for the rough structure,
and [this one](https://www.youtube.com/watch?v=5K4le-zJhfQ) for the modern Google Apps Script
development.

My first step was to create a dummy GitHub account,
[lintrans-issues-bot](https://github.com/lintrans-issues-bot), which only exists to create issues.
The anonymous issues will need a GitHub account to be created under. You could use your own but I
wanted a dedicated account. If you choose to use a separate account, it needs push access on the
repo to add assignees and labels to an issue.

I created a Google Form to match the issue templates. I started with just the bug report and then
repeated the process for feature suggestions. After creating the Form, click the 3 dots, and go to
"Script editor".

Go to add a library on the left and use the ID
`1B7FSrk5Zi6L1rSxxTDgDEUsPzlukDsi4KGuTMorsTQHhGBzBkMun4iDF`. This is for OAuth2.

I tweaked [this
code](https://github.com/St3ph-fr/my-apps-script-utils/blob/8e200020504a0a4676fcdd767fd6dbf6b123af6c/anonymous-issues-github/Code.js)
(see `*.js` files in this directory) to create a script for myself and created an OAuth application
with `lintrans-issues-bot`. The "Homepage URL" didn't seem to matter. The "Authorization callback
URL" needs to be `https://script.google.com/macros/d/SCRIPT_ID/usercallback` where `SCRIPT_ID` is
the ID of the Apps Script project (found in the URL), *NOT* the ID of the Form itself.

Now, in the Apps Script editor, select `setupAuthorization` as the function to run, and run it.
Paste the link into a new tab (make sure you're signed in with the GitHub and Google accounts that
you want to use for this step; I don't know if it matters, but I think it does) and authorize the
app.

Do the same thing with `getActiveFormPermission`. Google needs your permission to call
`FormApp.getActiveForm()` somewhere in the background, so doing it manually allows us to give that
permission for later.

In the Apps Script editor, go to "Triggers" on the left and setup a trigger to run `onFormSubmit`
when the form is submitted. You will probably need to authorize your own app. Thanks Google.

Now you're done!
