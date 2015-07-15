# Support Add-on for Hyperbaseline
- **Authors**:		Simon Balz <simon@balz.me>, Mika Borner <mika.borner@gmail.com>, Christoph Dittmann <mulibu.flyingk@gmail.com>, Harun Kuessner <h.kuessner@posteo.de>
- **Description**:	Store baseline statistics based on historical data and score current events based on these statistics
- **Version**: 		0.1

## Introduction
The Support Add-on for Hyperbaseline provides two custom search commands which enables the user to store statistical values in a splunk collection based on historical events (fillbaseline) and use these statistics to determine potential outliers in current data (comparetobaseline).

## Features
- store statistics in a splunk collection using fillbaseline
- compare events against statistics using comparetobaseline

## Additional Notes for Apptitude App Contest
- The app uses only portable code and is tested thoroughly on *nix and Windows systems.
- The app will be used within customer projects, and improved according to customer and community needs. Development of the app will happen in public. Bugs/Issues and improvement requests can be opened on the project's Github page (<https://github.com/my2ndhead/SA-hyperbaseline/issues>).

## Release Notes
- **v0.1**	/ 	2015-07-15
	- first initial version committed to github in develop branch

## Credits
- Ron Pearson (http://www.r-bloggers.com/author/ron-pearson-aka-thenoodledoodler/) for his blog about outler detection in R [5]

## Prerequisites
- Splunk v6.2+ (we use the App Key Value Store)

## Installation
1. Download the [latest](https://github.com/my2ndhead/SA-hyperbaseline/archive/master.zip) add-on
2. Unpack and upload the add-on to the search head
   IMPORTANT: Make sure, the App's folder name in $SPLUNK_HOME/etc/apps is SA-hyperbaseline (Downloading apps from git and uploading them to Splunk will result in wrong folder names)
3. Restart Splunk

### Note for distributed environments
- The alert manager runs mostly on the search head (since we use the App Key Value Store)
- Due to the usage of the App Key Value Store, there's no compatibility with Search Head Clustering (SHC) introduced in Splunk v6.2

## Roadmap
- add further outlier detection methods which are able to take seasonality and trend into account

## Known Issues
- the outlier detection doesn't take seasonality and trend into account
- statistics are not automatically removed from the collection. Erroneous data must be deleted manually

## License
- **This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.** [1]
- **Commercial Use, Excerpt from CC BY-NC-SA 4.0:**
  - "A commercial use is one primarily intended for commercial advantage or monetary compensation."
- **In case of Support Add-on for Hyperbaseline this translates to:**
  - You may use Support Add-on for Hyperbaseline in commercial environments for handling in-house Splunk alerts
  - You may use Support Add-on for Hyperbaseline as part of your consulting or integration work, if you're considered to be working on behalf of your customer. The customer will be the licensee of Support Add-on for Hyperbaseline and must comply according to the license terms
  - You are not allowed to sell Support Add-on for Hyperbaseline as a standalone product or within an application bundle
  - If you want to use Support Add-on for Hyperbaseline outside of these license terms, please contact us and we will find a solution

## References
[1] http://creativecommons.org/licenses/by-nc-sa/4.0/
[2] https://en.wikipedia.org/wiki/Median_absolute_deviation
[3] https://en.wikipedia.org/wiki/Quartile
[4] https://en.wikipedia.org/wiki/Medcouple
[5] http://www.r-bloggers.com/finding-outliers-in-numerical-data/
