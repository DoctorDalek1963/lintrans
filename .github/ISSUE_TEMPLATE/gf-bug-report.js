// vim: set et sw=2 ts=2:
const CLIENT_ID = "";
const CLIENT_SECRET = "";

/**
 * Get the response and submit it (run as submit trigger)
 *
 * Create a trigger by going to Resources > Current project's triggers
 * Select function onFormSubmit() and create a trigger at form submission
 */
function onFormSubmit(e) {
  var responseData = {
    "Bug report title": "",
    "Description": "",
    "Reproduction steps": "",
    "Crash report": "",
    "Contact details": ""
  };

  var itemResponses = e.response.getItemResponses();

  for (var i = 0; i < itemResponses.length; i++) {
    var itemTitle = itemResponses[i].getItem().getTitle();
    var itemResponse = itemResponses[i].getResponse();

    responseData[itemTitle] = itemResponse;
    Logger.log(itemTitle + ': ' + itemResponse);
  }

  try {
    var issue = submitIssue(responseData);
    var body = "<p>Hi,</p><p>Thank you for submitting your bug report, you can follow it on <a href='" + issue.html_url + "'>this page</a>.</p>";

    GmailApp.sendEmail(Session.getEffectiveUser().getEmail(), 'Bug report submitted on GitHub', '', {
      htmlBody: body,
    });

  } catch(e) {
    GmailApp.sendEmail(Session.getEffectiveUser().getEmail(), 'Error with bug report submission', '', {
      htmlBody: JSON.stringify(responseData),
    });
  }
}

/**
 * Get the body of the issue
 */
function getIssueBody(data) {
  crash_report = data['Crash report'] !== '' ?
    '```\n' + data['Crash report'] + '\n```\n' :
    '*No response*'

  contact_details = data['Contact details'] !== '' ?
    data['Contact details'] :
    '*No response*'

  return `### Description

${data['Description']}

### Reproduction steps

${data['Reproduction steps']}

### Crash report

${crash_report}

### Contact details

${contact_details}`
}

/**
 * Submit the issue on GitHub
 */
function submitIssue(data) {
  var service = getService();

  if (service.hasAccess()) {
    var url = 'https://api.github.com/repos/DoctorDalek1963/lintrans/issues';
    var apiRequestBody = {
      "title": "[Bug] " + data["Bug report title"],
      "body": getIssueBody(data),
      "assignees": ['DoctorDalek1963'],
      "labels": ['bug']
    };

    var response = UrlFetchApp.fetch(url, {
      method: "post",
      headers: {
        Authorization: 'Bearer ' + service.getAccessToken()
      },
      payload: JSON.stringify(apiRequestBody)
    });

    var result = JSON.parse(response.getContentText());
    Logger.log(JSON.stringify(result, null, 2));

    return result;

  } else {
    var authorizationUrl = service.getAuthorizationUrl();
    Logger.log('Open the following URL and re-run the script: %s', authorizationUrl);
  }
}


/**
 * Authorize and make a request to the GitHub API
 */
function setupAuthorization() {
  var service = getService();

  if (service.hasAccess()) {
    var url = 'https://api.github.com/user/repos';
    var response = UrlFetchApp.fetch(url, {
      headers: {
        Authorization: 'Bearer ' + service.getAccessToken()
      }
    });

    var result = JSON.parse(response.getContentText());
    Logger.log(JSON.stringify(result, null, 2));
  } else {
    var authorizationUrl = service.getAuthorizationUrl();
    Logger.log('Open the following URL and re-run the script: %s', authorizationUrl);
  }
}


/**
 * Get permission to call FormApp.getActiveForm (which we never call, but Google wants anyway)
 */
function getActiveFormPermission() {
  FormApp.getActiveForm();
}


/**
 * Configure the service
 */
function getService() {
  return OAuth2.createService('GitHub')
      // Set the endpoint URLs
      .setAuthorizationBaseUrl('https://github.com/login/oauth/authorize')
      .setTokenUrl('https://github.com/login/oauth/access_token')

      // Set the client ID and secret
      .setClientId(CLIENT_ID)
      .setClientSecret(CLIENT_SECRET)

      // Set the name of the callback function that should be invoked to complete
      // the OAuth flow
      .setCallbackFunction('authCallback')

      // Scope for the app
      .setScope('repo')

      // Set the property store where authorized tokens should be persisted
      .setPropertyStore(PropertiesService.getUserProperties());
}

/**
 * Handle the OAuth callback
 */
function authCallback(request) {
  var service = getService();
  var authorized = service.handleCallback(request);

  if (authorized) {
    return HtmlService.createHtmlOutput('Success!');
  } else {
    return HtmlService.createHtmlOutput('Denied');
  }
}
