# Greystone Labs Coding Challenge

Overview:

This project is a REST API for a Loan Amortization app using the Python miniframework FastAPI. It implements 6 endpoints:
- create user
- create loan 
- fetch loan amortization schedule
- fetch loan summary for a given month
- fetch all loans for a user
- share a loan with another user

To get this project running:
- After pulling down the repo and navigating to the top level directory of this project, be sure to run `source venv/bin/activate` to activate the virtual environment
- To start your FastAPI server, you can run Uvicorn with the command `uvicorn app.main:app --reload`


Future improvements: 

While I strived to follow best practices across this entire project, there are certain things that can still be improved, and that I would have liked to improve given a longer timeline for completion:
- Implement `lifespan` events currently recommended by FastAPI's docs [https://fastapi.tiangolo.com/advanced/events/] rather than the deprecated `.on_event` the app is currently using for startup.
- Refactor test_main.py to use fixtures for user and loan creation rather than creating new User and Loan records manually for each test
- Add model validation for loan creation to validate that amounts, loan terms, and interest rates must be positive values.


Other considerations:

- Readability depending on the use case for endpoints: 
    - While all of the endpoints return what they need to, the create_loan and fetch_loans_for_user endpoints both return amounts and interest rates with the full decimal precision they were created with (6 and 5 decimal places, respectively). Depending on what purpose these endpoints serve, it might be preferable to update the response body to a more human-readable format, with only 2 or even 0 decimal places. Potentially we may want to add more formatting, such as a `$` to prefix all dollar amounts returned and/or a `%` sign following interest rates. If this API were built for production, it would be important to consider whether these endpoint response bodies were being used, for example, for further calculations or being passed into a UI for a customer to view; this would affect whether an endpoint should return a rounded value, or an unrounded Decimal with full precision.

- Decimals vs. Integers:
    - I used Python's Decimal class for precision, as floats, though easier to implement, can be imprecise, and are not recommended for use with financial data. Another option was to use integers for loan amounts and interest rates, and to record amounts in the database as cents. Integers are faster computationally on average than Decimals, but Decimals are easier to implement and more intuitive to use. If I went the integer route, I would want to create a custom Money class in order to create a more intuitive experience for working with integers as money for both developers and end users. Decimals are easier to implement, and since this app doesn't require very performant data, isn't doing a huge volume of transactions, and Decimals here are mostly being used for internal calculations, Decimals were a suitable choice for this project. However, if I were building this for production, I would lean more towards using integers, especially if the app was likely to be doing a high volume of transactions.

- Rounding options:
    - My amortization calculations are using the default rounding method for Python's Decimal class, which is known as banker's rounding; this type of rounding is common in financial calculations to reduce cumulative rounding errors, though there are other options for rounding methods. Another possibility is ROUND_HALF_UP, which is the type of rounding most people learn in school and are most familiar with. Depending on the preferences of the org and the standards they're held to for regulatory or compliance reasons, either banker's rounding or ROUND_HALF_UP could be more suitable for calculations such as loan amortization.

- Sign-in & Authentication:
    - As sign-in and authenticaion were not requirements of this project, this API was built without consideration for user or authorized agent authentication. This is obviously a huge shortcoming of the app, and these features would need to be built out to support this API if it were running in production. Users should only be able to see endpoint data that pertains to themselves.

- Question on loan schedule usage:
    - For the loan schedule endpoint, would there ever be a need to see the loan schedule for a hypothetical loan that didn't belong to a user or exist in the database yet? If so, the endpoint would need to be updated to accept the parameters of a loan itself (amount, interest rate, term) rather than an loan_id as it is built to do so now.
