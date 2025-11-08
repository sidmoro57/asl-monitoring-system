# Browser Scripts for Monitoring Systems

This document provides comprehensive information about browser scripts that can enhance monitoring and operational safety for web applications, with a focus on the Isengard AWS Banner as a reference implementation.

## Table of Contents

1. [Isengard AWS Banner](#1-isengard-aws-banner)
2. [Pre-prod Federation](#2-pre-prod-federation)
3. [Installation Guide](#installation-guide)
4. [Troubleshooting](#troubleshooting)
5. [Best Practices](#best-practices)

---

## 1. Isengard AWS Banner

### What is it?

This script places a banner at the top of your AWS Console – showing the email and account ID of the Isengard account you have federated into, as well as if the account is a production or not.

![Banner Example - Standard](https://code.amazon.com/screenshots/banner-standard.png)

![Banner Example - Production](https://code.amazon.com/screenshots/banner-production.png)

**Production Account Warning:** If the account is marked as Production, the banner will change to a very scary red color to provide a strong visual warning.

**Additional Features:**
- If AWS is under a Change Control Day, or there is an LSE, you will see these messages on the top right corner
- The script displays the federated role name in the banner
- For Production accounts, it disables the 'Delete' stack button in the CloudFormation Console

![Change Advisory Banner](https://code.amazon.com/screenshots/change-advisory.png)

### Why do I need it?

We are hoping this will reduce the confusion that can come with federating into many Isengard accounts. Hopefully it can prevent operator errors that can arise from unknowingly making changes to Production Isengard accounts in the AWS Console.

### How do I install it?

#### Chrome

1. Install the Tampermonkey Chrome extension:
   - From [Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey)
   - Or from [tampermonkey.net](https://www.tampermonkey.net/)

2. Enable Developer mode:
   - Go to `chrome://extensions`
   - Find Tampermonkey and expand its details
   - Enable the "Allow User Scripts" toggle at the top right
   - See [Tampermonkey's official guidance](https://www.tampermonkey.net/faq.php)

**Note:** TamperMonkey in Firefox does not load on the console home page, but works on other pages. GreaseMonkey works on all pages.

#### Firefox

Install the GreaseMonkey script manager extension:
- [GreaseMonkey for Firefox](https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/)

#### Install the Script

1. After the extension is installed, go to the script URL:
   ```
   https://isengard.amazon.com/isengard-aws-banner.user.js
   ```
   (or append `/isengard-aws-banner.user.js` for MVP)

2. If you lack permissions:
   - You'll need your manager to add you to the source code
   - Visit: https://permissions.amazon.com/group.mhtml?group_type=posix&group=source-code-misc

3. Click "Install" when prompted

![Installation Screen](https://code.amazon.com/screenshots/install-screen.png)

4. The tab should close and the script is installed

### Do I need to manage the script myself?

Nope! Assuming you download the script using the link above and you are on a relatively new version of GreaseMonkey/TamperMonkey, the script will update itself whenever there is a new version.

### Why are you making me install the script? Why can't it just work?

This script adds some elements to the AWS Console. Unfortunately, we do not have the ability to make direct changes there. Therefore, we need to utilize browser scripts to add the elements for us.

### What if I have questions, concerns, or ideas?

You can reach out to us via email: isengard-team@amazon.com

### Current Error

If you are getting an error, please uninstall the script and redownload it from the URL mentioned above.

![Error Screenshot](https://code.amazon.com/screenshots/error-1645031195959-670.png)

### Change Log

**Code Repository:** https://code.amazon.com/packages/IsengardUIStaticWebsite/blobs/mainline/--/public/isengard-aws-banner.user.js#bypass=true

#### Version 2.0
- **Code Review:** https://code.amazon.com/reviews/CR-23518127/revisions/2#/details
- Remove #f styling that broke language selection
- Verified footer still displays on pages it previously addressed

#### Version 1.9
- **Code Review:** https://code.amazon.com/reviews/CR-23055856/revisions/1#/details
- Fix Change Advisory Text rendering as text instead of HTML

#### Version 1.8
- **Code Review:** https://code.amazon.com/reviews/CR-22056747/revisions/1#/details
- Update the definition of Prod to be solely based on `is_production` field

#### Version 1.7
- **Code Review:** https://code.amazon.com/reviews/CR-21983327/revisions/1#/details
- Adds additional clarifying text on clicking the delete stack button when disabled
- Lets the user know it was the banner that disabled the action

#### Version 1.6
- **Code Review:** https://code.amazon.com/reviews/CR-21972549/revisions/1#/details
- Fixes bug in Firefox where Isengard banner was appearing more than once in EC2 Console
- Fixes other pages where GM loaded more than once

#### Version 1.5
- Adds a banner to the AWS Console with useful information
- Disables the 'Delete' stack button in the CloudFormation Console for Production accounts
- **Reference:** https://sim.amazon.com/issues/CFN-31272

#### Version 1.4
- Fixes for certain consoles where the banner didn't appear properly

#### Version 1.3
- Fix for a CSS issue with Polaris consoles

#### Version 1.2
- Add the federated role name to the banner

#### Version 1.1
- PDT Support
- LSE Integration
- Firefox Quantum / GreaseMonkey 4+ Support
- CSS/HTML Cleanup

#### Version 1.0
- Initial release

---

## 2. Pre-prod Federation

### Summary

This feature allows users to use existing production Isengard console access roles to federate into the pre-production AWS Console by requesting credentials from the Testing Sign-in endpoint and redirecting to the Integ ConsoleProxy endpoint.

### Scripts

- **Install Script:** https://code.amazon.com/packages/IsengardBrowserScripts/blobs/mainline/--/isengard-pre-prod-federation.user.js?raw=1
- **Source Code:** https://code.amazon.com/packages/IsengardBrowserScripts/blobs/mainline/--/isengard-pre-prod-federation.user.js

**Permissions:** If you lack permissions, you'll need your manager to add you to the source code:
https://permissions.amazon.com/group.mhtml?group_type=posix&group=source-code-misc

### What is it?

It allows users to use temporary credentials and federate into the pre-prod AWS Console stack.

#### Getting Started

To get started, click the temporary credentials button, next to the role that you want to federate with.

![Getting Started](https://code.amazon.com/screenshots/getting-started.png)

#### Without the script

Without the script, the user is unable to use the feature:

![UX without GreaseMonkey script](https://code.amazon.com/screenshots/without-script.png)

#### With the script

With the script, the user can use the feature:

![UX With GreaseMonkey script](https://code.amazon.com/screenshots/with-script.png)

### Why do I need it? Can't it just work?

Unfortunately, some of the necessary technical components are not in-place currently. We have a long-term goal of fully supporting this native functionality, but in order to get the feature to customers as soon as possible, we created this solution.

---

## Installation Guide

### Prerequisites

- Modern web browser (Chrome or Firefox recommended)
- Browser extension manager (Tampermonkey for Chrome, GreaseMonkey for Firefox)
- Appropriate permissions to access source code repositories

### Step-by-Step Installation

#### For Chrome Users

1. **Install Tampermonkey:**
   ```
   Navigate to: chrome://extensions
   Search for "Tampermonkey" in Chrome Web Store
   Click "Add to Chrome"
   ```

2. **Configure Tampermonkey:**
   ```
   Go to: chrome://extensions
   Find Tampermonkey
   Enable "Allow User Scripts"
   ```

3. **Install the Script:**
   - Visit the script URL
   - Click "Install" when prompted
   - Confirm installation

#### For Firefox Users

1. **Install GreaseMonkey:**
   ```
   Navigate to: about:addons
   Search for "GreaseMonkey"
   Click "Add to Firefox"
   ```

2. **Install the Script:**
   - Visit the script URL
   - Click "Install" when prompted
   - Confirm installation

### Verification

After installation:
1. Navigate to the AWS Console
2. Verify that the banner appears at the top of the page
3. Check that account information is displayed correctly
4. For production accounts, verify that the banner is red

---

## Troubleshooting

### Common Issues

#### Script Not Loading

**Symptoms:**
- Banner does not appear in AWS Console
- No visual changes to the console

**Solutions:**
1. Verify that the browser extension (Tampermonkey/GreaseMonkey) is installed and enabled
2. Check that "Allow User Scripts" is enabled (Chrome)
3. Refresh the AWS Console page
4. Reinstall the script from the official URL

#### Banner Appears Multiple Times (Firefox)

**Symptoms:**
- Multiple banners appear on the same page
- Banner duplicates when navigating between console pages

**Solutions:**
- Update to Version 1.6 or later
- This issue was fixed in Version 1.6

#### Delete Button Still Enabled in Production

**Symptoms:**
- CloudFormation delete stack button is not disabled in production accounts

**Solutions:**
1. Verify that the account is correctly marked as Production in Isengard
2. Check account "data classification" on the "View/Edit" page
3. Update to Version 1.8 or later for correct production detection

#### Language Selection Not Working

**Symptoms:**
- Cannot select language in AWS Console
- Language dropdown is not responsive

**Solutions:**
- Update to Version 2.0 or later
- This issue was fixed by removing conflicting #f styling

#### Change Advisory Text Not Displaying Properly

**Symptoms:**
- Change advisory messages appear as plain text instead of HTML
- Formatting is incorrect

**Solutions:**
- Update to Version 1.9 or later
- This issue was fixed in Version 1.9

### Getting Help

If you encounter issues not covered in this troubleshooting guide:

1. **Check the version:** Ensure you have the latest version of the script
2. **Reinstall:** Uninstall and reinstall from the official URL
3. **Contact support:** Email isengard-team@amazon.com
4. **Permissions:** Verify you have appropriate access permissions

---

## Best Practices

### Security Considerations

1. **Only install from official sources:**
   - Use only the official script URLs
   - Verify the source before installation
   - Do not modify the script unless you understand the implications

2. **Keep scripts updated:**
   - Enable automatic updates in your browser extension
   - Regularly check for new versions
   - Review change logs for security updates

3. **Review permissions:**
   - Understand what permissions the script requires
   - Only grant necessary permissions
   - Regularly audit installed scripts

### Operational Best Practices

1. **Production Account Safety:**
   - Always verify the banner color before making changes
   - Red banner = Production account - Exercise extreme caution
   - Use the banner as a visual reminder of the environment

2. **Role Identification:**
   - Pay attention to the federated role name displayed in the banner
   - Verify you're using the correct role for your task
   - Escalate privileges only when necessary

3. **Change Control Awareness:**
   - Monitor for Change Control Day notifications
   - Check for LSE (Large Scale Event) messages
   - Follow organizational policies during restricted periods

4. **Multi-Account Management:**
   - Use the banner to prevent confusion between accounts
   - Develop a habit of checking the banner before making changes
   - Keep a reference list of your frequently used accounts

### Development and Maintenance

1. **Testing:**
   - Test script updates in non-production environments first
   - Verify functionality across different console pages
   - Check compatibility with browser updates

2. **Documentation:**
   - Keep internal documentation updated
   - Document any customizations or configurations
   - Share knowledge with team members

3. **Feedback:**
   - Report bugs and issues to the development team
   - Suggest improvements based on usage patterns
   - Participate in user testing when available

### Browser Extension Management

1. **Regular Maintenance:**
   - Keep browser extensions updated
   - Remove unused scripts
   - Review extension permissions periodically

2. **Performance:**
   - Monitor browser performance
   - Disable unnecessary scripts
   - Report performance issues

3. **Compatibility:**
   - Test with major browser updates
   - Verify compatibility with other extensions
   - Keep browser extension managers updated

---

## Related Documentation

### Tags

- Isengard Triforce
- AWS Console Management
- Browser Automation
- Security & Compliance
- Operational Safety

### Referenced By

The following teams and resources reference this documentation:

- AWS.Lattice.Operations.On-Call
- App Mesh OnCall
- AWS.Mobile.DeepDish.Projects.Gogi.Operations.Runbook
- AWS.Solutions.SolutionsTeam.Teams.Berryessa.TeamOnboarding
- AWS242.DeveloperLaunchPlan
- AWSControlTower.OnCall.GoingOnCall
- AmazonMQ.NewHireV2.DevSetup
- BuilderTools.Product.LicenseService.Operations.Runbooks
- Cassowary.DeveloperGuide.Tooling
- DataZone.Team.Administration.Operations.OncallGuidance
- DataZone.Team.Catalog.Operations.OncallGuidance
- Dodrio.ProductivityTools
- DuckHawk.DeveloperGuide.Tooling
- GameLiftStreams.Runbooks.Oncall
- InfraMap.Cloud.Resources
- Lily.Nexus.TeamOnboarding
- RDS.PlatformFrontendSydney.Onboarding
- Schapper.Tooling.Ubuntu
- SideStep.Development.Tools
- StreamLift.Oncall
- Switchboard.ApplicationAccess.NewHire
- TEAMRNG.OnCall.GoingOnCall
- Users.allyrm.Onboarding (QuickSight Embedding Onboarding)
- Users.kvinsu
- Users.mikjager.IsengardTips

### Additional Resources

- **Isengard Documentation:** https://isengard.amazon.com/docs
- **AWS Console Documentation:** https://docs.aws.amazon.com/console/
- **Tampermonkey Documentation:** https://www.tampermonkey.net/documentation.php
- **GreaseMonkey Documentation:** https://wiki.greasespot.net/

---

## Support

For questions, concerns, or ideas:
- **Email:** isengard-team@amazon.com
- **Internal Wiki:** Search for "Isengard AWS Banner" on your internal wiki
- **Code Repository:** https://code.amazon.com/packages/IsengardUIStaticWebsite

---

*This documentation is maintained as part of the ASL Monitoring System repository as a reference implementation for browser-based monitoring and safety features.*

*Last Updated: 2025-11-08*
