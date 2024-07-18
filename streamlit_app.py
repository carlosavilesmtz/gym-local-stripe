import streamlit as st
from st_paywall import add_auth
import stripe
from sqlalchemy import text

# Set up Streamlit page configuration
st.cache_data.clear()
st.set_page_config(layout="wide", page_title="Streamlit App", page_icon=":tada:", initial_sidebar_state="auto", menu_items=None)

# Define a function to get the Stripe customer ID based on email
def get_customer_id(email):
    # Use Stripe API to list customers with the given email
    customers = stripe.Customer.list(email=email).auto_paging_iter()
    # Iterate through the customers and return the ID if a match is found
    for customer in customers:
        return customer['id']
    # If no customer is found, return None
    return None

# Define a function to cancel a subscription based on email
def cancel_subscription(email):
    # Get the Stripe customer ID associated with the email
    customer_id = get_customer_id(email)
    
    # Use Stripe API to list subscriptions for the customer
    subscriptions = stripe.Subscription.list(customer=customer_id).auto_paging_iter()
    # Iterate through the subscriptions
    for subscription in subscriptions:
        # Check if the subscription is not already canceled
        if subscription['status'] != 'canceled':
            # Check if the subscription is already scheduled to be canceled at the end of the period
            if subscription['cancel_at_period_end']:
                st.write(
                    f"Your subscription {subscription['id']} was already accepted to be canceled after the end of the period.")
            # If the subscription is not scheduled to be canceled, cancel it
            else:
                stripe.Subscription.modify(
                    subscription['id'],
                    cancel_at_period_end=True,
                )
                st.write(f"Subscription {subscription['id']} will be canceled at the end of the current period.")

# Set the title of the Streamlit app
st.title("Mi GYM! 🚀")

# Establish a connection to the MySQL database
conn = st.connection('mysql', type='sql')

# Query the gym_subs table to get all subscription data
gym_subs = conn.query('select * from gym_subs', ttl=100)

# Display the subscription data in a table format
st.dataframe(gym_subs)
st.write(gym_subs)

# Use the st_paywall library to handle user authentication and subscription
add_auth(required=True)

# This section of code will only be executed after the user has authenticated and subscribed
# The email and subscription status are stored in the Streamlit session state
email = st.session_state.email

# Query the gym_subs table to check if the user's email exists
sub = conn.query('SELECT email FROM gym_subs WHERE email="'+email+'"')
st.write(sub['email'])

# If the user's email is not found in the database, add the user to the gym_subs table
if (sub['email']).empty:
    with conn.session as session:
        # Execute an SQL query to insert the user's email and subscription status into the gym_subs table
        session.execute(text("INSERT INTO gym_subs (email, subscription) VALUES (:email, :subscription);"), {"email":email, "subscription":1})
        # Commit the changes to the database
        session.commit()
    # Clear the Streamlit cache to reflect the changes
    st.cache_data.clear()
    # Display a success message to the user
    st.write("Subscription added successfully!")
# If the user's email is found in the database, display a welcome message
else:
    st.write(f'Welcome!'+email+'!')

# Display the current session state
st.write(st.session_state)

# Initialize a confirmation flag in the session state
if 'confirm' not in st.session_state:
    st.session_state.confirm = False

# Display a button to initiate the subscription cancellation process
if st.button('Cancel subscription'):
    # Toggle the confirmation flag
    st.session_state.confirm = not st.session_state.confirm

# If the confirmation flag is set, display a confirmation button to proceed with cancellation
if st.session_state.confirm:
    # Display a confirmation button
    if st.button('Are you sure you want to cancel sub?'):
        # Cancel the user's subscription
        cancel_subscription(email)
        # Reset the confirmation flag
        st.session_state.confirm = False

# Display the user's subscription status
st.write(f"Subscription Status: {st.session_state.user_subscribed}")

# Display a success message if the user is subscribed
st.write("🎉 Yay! You're all set and subscribed! 🎉")

# Display the user's email address
st.write(f'By the way, your email is: {st.session_state.email}')
