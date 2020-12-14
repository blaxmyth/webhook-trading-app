#Tradier API Account Creds
ACCOUNT_ID = 'VA41833079'
ACCESS_TOKEN = 'Q08gROJzMtbjiun3aBAdavJQXGpS'

PROD_TOKEN = 'YZnC1KzkrzizOgOkp82YR3wwG3ON'

#Amazon SES SMTP Creds
SMTP_USERNAME = 'AKIAV3GMUI755TDID4G5'
SMTP_PASSWORD = 'BNifvvCgK6OK3eqRfwddwMaEXVd1b53t8TAnBMkXsika'

base_url = "https://sandbox.tradier.com" #initialize base url

headers = {'Authorization': 'Bearer {}'.format(ACCESS_TOKEN), 'Accept': 'application/json'} #initialize headers for http requests