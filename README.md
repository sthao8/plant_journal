PLANT JOURNAL
### Video Demo: [Youtube Video](https://youtu.be/BaNxcV-AOuY)
### Description:
#### Purpose:
Plant Journal aims to simulate a physical journal for keeping track of users' plants, and when and how they've interacted with their plants. From a plant's page in the journal, users can see the last time the plant was repotted, treated, watered, or fertilized to determine when to schedule these events in the future. Death of plant events can help document what to avoid in the future since the additional notes field can aid in remembering observations in general.
#### Features:
- Client-side indicators help visually show users password requirements met or still needed while server-side checks ensure password validity before creating accounts.
- Adding plants to a journal is simple via the lookup feature where a third-party API provides an image and some basic information to help users find their plant.
- Table of content page allows users to quickly see an overview of their plants and how much time has passed since the last update so it's easy to know which plants have perhaps been neglected.
- Responsive webpage looks great on multiple screen sizes.
- Search results are divided into 10 per page for less scrolling, and easy navigation is provided with a sticky-bottom pagination navbar.
- Informative error page with custom messages lets users know what went wrong.
#### Technologies:
- Relational database programmed with SQLite3.
- Frontend developed with HTML, Bootstrap 5.3, and Javascript.
- Backend developed with Python 3.12.0, Flask 3.0.0, and Jinja2.
- Plant information provided by querying third-party API, [House-Plants API on rapidapi.com](https://rapidapi.com/mnai01/api/house-plants2/).
- Password encryption via werkzeug.security.
#### Dependencies (included in requirements.txt):
- CS50's library
- Flask
#### Resources used in video demo:
- Avatar image by [Ksenia Chernaya on pexels.com](https://www.pexels.com/photo/cacti-on-brown-wooden-shelves-3952032/).
- Background image by [Bruno Cervera on pexels.com](https://www.pexels.com/photo/long-green-cacti-on-pink-background-6032875/).
- Placeholder image by [Dominika Roseclay on pexels.com](https://www.pexels.com/photo/two-white-flower-vases-2146109/), edited by me.
- Icon made with [Favicon](https://favicon.io/).
#### How to install:
1. Download or clone this repo from github onto your computer.
2. Navigate to the downloaded/cloned folder in the development environment of your choice and open the folder.
3. Run `pip install -r requirements.txt` in the terminal to install dependencies. (You may find this [link](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) helpful.)
4. Run `flask run` in the terminal to start the Flask application. You may find this [link](https://flask.palletsprojects.com/en/3.0.x/quickstart/) interesting.
5. CTRL-click the generated link from step 4 to open Plant Journal in a browser.
6. You should now see the landing page of Plant Journal in the browser.
#### How to use:
1. Register for an account on Plant Journal and log in. Take care to choose a unique username and fulfill all password requirements.
2. Add a plant via Add Plant. You may type in the name of your plant (common or latin name, eg "Boston Fern" or "Nephrolepis exaltata") or the category if you don't know the name, eg "fern" or "cactus." You may select from the dropdown to choose an alias from the pre-populated common names or enter a custom nickname. A plant alias is a unique identifier in your journal for your plant. If you have two Boston Ferns, you must choose two different names, eg. "Boston Fern1" and "Boston Fern2." The date field here is mandatory, but the rest of the form is optional.
3. Add journal entries each time you interact with your plant via the Write Journal Entry button on the plant's journal page. Selecting the event type (like "watering", or "fertilizing") is mandatory, as well as the date of the event, but the notes field here is optional. You can use it to store observations or things you would like to remember in the future, such as "used 1/3 strength cactus fertilizer" or "Need to repeat this Blamo treatment every 3 weeks."
#### Set up fresh database (optional):
This repo comes with a plants.db relational database that holds entries from testing and development with the following tables:
- users table consisting of id, username, and a hash of user's password
- plants table consisting of an id for each unique plant added by all users, its latin name, and the ID used by the thrid-party API used to query API for only that plant
- intake_details table consisting of ids for each added plant, unique id combination of owner ID (user ID) and plant alias, plant id (from the plants table) to retrieve plant's latin name and API ID, date plant was acquired, as well as the optional information entered by user such as acquire method, acquired from, and optional notes
- event_type table that is auto-populated with set values for, eg., "Acquired", "Watering" (and so on), strings that are associated with emojis assigned in app.py on line 382
- event_history table, which is populated with each journal entry and consists of an id per entry, owner_id (user id), plant alias, event type from the event_type table, additioanl details user optionally offers, event date, and the entry date that automatically logs when the entry was made.

This default database holds demo accounts with password "Password1!" and usernames found in the video demo. If you would like to delete the existing plants.db and create a fresh database, follow these steps:
1. SQLite3 comes with python, but you may need to install command-line tools. Read more [here](https://www.sqlite.org/cli.html) and download from [here](https://www.sqlite.org/download.html).
2. Within the command line with SQLite3 open as per step 1, open your new database called plants.db. Otherwise, if you choose to name your database differently, replace line 19 in app.py with your new database name (db = SQL("sqlite:///_your_database_name_.db")).
3. Copy and paste the contents of plants.sql found in the project folder into SQLite3 in the command line. Press Enter.
4. Confirm that the schema matches the schema in plants.sql by running this command: `.schema`.
5. Confirm that event_type table is correctly set up by running this command: `SELECT * FROM event_type;` which should return these results:
    - 1|Acquired
    - 2|Watering
    - 3|Fertilizing
    - 4|Treatment
    - 5|Repotting
    - 6|Death
6. Delete the old plants.db (or optionally, you may want to rename plants.db to plants.db.bak in case anything goes wrong) and place your new database into the project folder where plants.db was/is.
### File Breakdown:
#### plants.db:
This is the database used to store information as described in detail [here](https://github.com/code50/123779845/tree/main/project#set-up-fresh-database-optional). It has test accounts and database entries accumulated during development. There were some design choices that were made initially that could do with revamping now that the project is more complete.

One such case is that each event type (eg."watering") was to be treated uniquely and would come with its own relevant user input just like the "acquired" event type asks for acquired method and acquired from. But later on, because no other event type featured event-specific input, it was simpler to normalize each event type and place all additional information into the additional_notes column in the event_history table, though at the cost of fine-grain retreival of user input. As a result, the intake_details table has extraneous columns like the acquired_from column, since this information is also copied into the event_history table and it is never extracted and used elsewhere not in conjunction with the other optional data in additional_notes. If, in future development, fine-grain usage of user input is needed, it would be better to keep these event-specific fields separate.

Another case of inefficient initial design is that emojis matching event type is defined inside app.py in the page-plant route since I wasn't sure which emoji to use and preferred not to do repeated INSERT/DELETE database statements while experimenting. But for more single-source-of-truth and better organized code, it would be better to have this information inside the event_type table in a column called emoji.
#### plants.sql:
This file is included to help users easily create a fresh plants.db.
#### requirements.txt:
Requirements.txt is a commonly used file containing any non-standard dependencies needed for a program to function. Users not familiar with CS50 should still be able to quickly install, set up, and use Plant Journal.
#### app.py:
This project follows the structure given in CS50 lecture and the finance pset. This file is where the python and Flask code lives. Here, Flask determines what each route should return and python is used for all of the logic like, for instance, checking password requirements were met in the register route, checking required inputs were entered in forms, querying the API and checking if API ID and latin name match when returned from client side, executing database statements, etc.
#### helpers.py:
This file contains functions used in multiple routes such as a login_required wrapper from the CS50 finance pset, some functions to query the third-party API, and a function to dynamically build SQL queries and execute them.
#### layout.html:
This file holds the shared template across all routes, including the Bootstrap CSS file, Bootstrap javascript, and the top navbar (which holds the login and register links when there is no user in session, else the logout link). Since login is a modal instead of a route, its code lives here as well, allowing users to stay on whichever page they are on when logging in. This file also sets up flashed messages, which is currently used once after account registration is complete.
#### register.html:
This is a standard register account page with the exception of password indicators that, upon keyup events in the first password input field, checks for fulfillment of password requirements. Since sneaky users can bypass the `required` tag on this field and the javascript that doesn't allow form to be submitted without all checks being completed, and since password checking ultimately occurs on the server side with python, these indicators are purely visual for the user's benefit.
#### lookup.html:
This page is analogous to going to google.com. Users get redirected here first when clicking Add Plant in the navbar in order to standardize the way plants are added (although due to limited use of API information, users could theoretically input their own plant latin name that doesn't exist in the API). This page contains a simple search form and works hand-in-hand with the next file, add-plant.html, since both have the ability to search (aka query the API using the lookup function).
#### add-plant.html:
This page returns the search results from lookup.html in sets of 10. There is a pagination navbar at the bottom that appears only if there are search results. Something to implement in the future would be to limit the amount of pages shown in the pagination navbar. The search bar is repeated here so users don't have to click on Add Plant link in the navbar if the plant they were looking for wasn't in the search results. On this page is also the form to add a plant with some pre-populated fields based on the plant the user is adding.

Something to note is that since Bootstrap dropdowns are not selects but rather inputs of unordered lists, there seems to be an uncaught exception raised when these dropdowns are triggered, as seen when using Chrome's Inspect. But no functional errors are otherwise apparent.
#### index.html:
This page displays various messages if user is not registered or if not plants are added. Otherwise it becomes the table of contents for user's plant journal listing each added plant by alias, their "page number" in journal, and time since that plant's last update.
#### plant-page.html:
This page features a currently non-functional image upload on the right-hand side. I didn't have time to fully research this feature and was concerned about security risks (maybe receiving malicious data from users), so right now it's just a placeholder. The left-hand side shows each journal entry for that plant, starting with the acquire event that is automatically generated when users add a plant. Here, users can add new journal entries by submitting the form that pops up when they click the Add Journal Entry button. When users have enough entries for a scroll bar to appear, upon refresh or loading the plant page, the scroll bar starts at the bottom position so that the newest journal entries are visible.
#### error.html:
This page is a simple error page displaying a wilted flower emoji and informative custom error messages.
#### styles.css:
This file contains style code used in Plant Journal, although some were added before I found Bootstrap classes that have the same functionality and thus not really necessary.
