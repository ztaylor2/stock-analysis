# Testing Plan

## Unit Tests

### Views

##### Landing Page home_view
    * All items appear on page as planned.

##### detail_view
    * When an inproper symbol is entered, a error is shown.
    * When a GET request happens, a proper response is returned.
    * When a POST request happens, it is transfered to all Upper case.
    * When a POST request happens, the proper date range is returned.
    * When a POST request happens, info for the proper stock is returned.
    * When a POST request happens, info for the proper price is returned.
    * The date is properly translated into 'Days ago.'
    * When a proper symbol is entered, authentic data is shown in graph.
        + LR:  fit meets expected outcome.
        + LR:  predict meets expected outcome.
        + SVR: fit meets expected outcome.
        + SVR: predict meets expected outcome.
    * When click on portfolio tab, it routes properly.
    * When 

##### portfolio_view
    * Currently chosen stocks appear for given user.
    * If user is not logged in, portfolio view can not be accessed.
    * Upon entering a valid symbol, and clicking add, that item is appended to table.
    * Upon entering a valid symbol, and clicking add, that item is also appended to database.
    * Upon entering an invalid symbol, proper error handling takes place.
    * When a remove "-" is selected, the appropriate stock is removed from the table.
    * When a remove "-" is selected, the appropriate stock is also removed from the database.
    * When view is refreshed or opened, fresh, updated info is provided for all listed stocks in user's portfolio.

##### Add stock to portfolio
    * Given invalid symbol, raises error.
    * Given valid symbol:
        + adds stock info to table.
        + Stock info visually appears.
        + Stock symbol is added to DB.

##### login
    * Given authenticated user, returns a HTTPFound redirect to the portfolio page.
    * Returns a page with only the entry field and "+" button.
    * Given incomplete data, raises error
    * Given complete but incorrect data, raises error

##### logout
    *Upon logging out, user's portfolio is no longer accessible.
    * returns a 302 response code
    * returns a HTTPFound redirect to the home page



## Functional Tests

### Routes

##### home - `/`
    * Has 200 response code
    * Has Get started, Login & Sign-up

##### detail - `/detail` 
    * Has 200 response code
    * Has stock symbol entry form field
    * Unauthenticated:
        + login option in Hamburger menu
    * Authenticated:
        + logout option in Hamburger menu
        + Portfolio option in Hamburger menu
    * When directed from Portfolio, incoming sybol is automatically chosen and displayed.

##### portfolio - `/portfolio`
    * has Logout & Detail views in hamburger menu.
    * Unauthenticated:
        + 403 forbidden
    * Authenticated:
        + With an empty portfolio (GET):
            + Has 200 response code
            + Has 1 empty form field and an " + " button.
            + If symbol is entered, proper data is added to table.
        + With items in portfolio (POST):
            + Has 200 response code
            + Displays appropriate amount of stock TRs in Tbl.
            + If symbol is entered, proper data is added to table.
            + When an existing item is chosen, user is sent to detail page for that item.

##### process_symbol - `/symbol`  ?????


##### login - `/login`
    * Unauthenticated:
        + response has 200 status code
        + form for username and password
    * Authenticated:
        + response has 302 code
        + redirects to portfolio page
        + user is still authenticated
        + Portfolio page still has logout and Detail options in hamburger menu.

##### logout - `/logout`
    * Unauthenticated:
        + 403 forbidden
    * Authenticated:
        + response has 302 status code
        + removed the auth_tkt cookie
        + redirects to the home page
        + home page has login button and no logout button
