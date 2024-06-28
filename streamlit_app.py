import streamlit as st
from st_paywall import add_auth
import stripe
st.set_page_config(layout="wide", page_title="Streamlit App", page_icon=":tada:", initial_sidebar_state="auto", menu_items=None)

def get_customer_id(email):
    customers = stripe.Customer.list(email=email).auto_paging_iter()
    for customer in customers:
        return customer['id']
    return None

def cancel_subscription(email):
    customer_id = get_customer_id(email)
    

    subscriptions = stripe.Subscription.list(customer=customer_id).auto_paging_iter()
    for subscription in subscriptions:
        if subscription['status'] != 'canceled':
            if subscription['cancel_at_period_end']:
                st.write(
                    f"Your subscription {subscription['id']} was already accepted to be canceled after the end of the period.")
            else:
                stripe.Subscription.modify(
                    subscription['id'],
                    cancel_at_period_end=True,
                )
                st.write(f"Subscription {subscription['id']} will be canceled at the end of the current period.")

st.title("Mi GYM! 🚀")
add_auth(required=True)

# ONLY AFTER THE AUTHENTICATION + SUBSCRIPTION, THE USER WILL SEE THIS ⤵
# The email and subscription status is stored in session state.

st.write(st.session_state)

email = st.session_state.email

if 'confirm' not in st.session_state:
    st.session_state.confirm = False

if st.button('Cancel subscription'):
    st.session_state.confirm = not st.session_state.confirm

if st.session_state.confirm:
    if st.button('Are you sure you want to cancel sub?'):
        cancel_subscription(email)
        st.session_state.confirm = False

st.write(f"Subscription Status: {st.session_state.user_subscribed}")
st.write("🎉 Yay! You're all set and subscribed! 🎉")
st.write(f'By the way, your email is: {st.session_state.email}')