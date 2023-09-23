import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, SentimentOptions
import datetime


# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    # If argument contain API KEY
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)

    return json_data

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    requests.post(url, params=kwargs, json=json_payload['review'])

    return print("Review posted", json_payload)

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    results = []
    json_result = get_request(url, id=dealer_id)
    if json_result:
        reviews = json_result
        for review in reviews:
            review_doc = review
            review_obj = DealerReview(dealership=review_doc["dealership"], name=review_doc["name"], purchase=review_doc["purchase"], 
                                    review=review_doc["review"], car_make=review_doc["car_make"], car_model=review_doc["car_model"],
                                    car_year=review_doc["car_year"], id=review_doc["id"], purchase_date=review_doc["purchase_date"],
                                    sentiment="sentiment")
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            if review_obj.purchase_date:
                review_obj.purchase_date = datetime.datetime.strptime(review_obj.purchase_date, '%m/%d/%Y')            
            results.append(review_obj)

    return results

# Create a get_dealer_by_id_from_cf method to get dealers from a cloud function by id
def get_dealer_by_id_from_cf(url, dealer_id, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=dealer_id)
    dealer = json_result

    return dealer

def get_dealers_by_state(url, state, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, state=state)
    dealers = json_result
    
    return dealers
            
# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
    url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/e9647bb4-2918-4acd-9d51-84c7ce9ef927"
    api_key = "WkMOfDRpUnFF9msEm2NZKeamAvGIc73AixHz0dKifuMv"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2022-04-07',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=dealerreview,features=Features(sentiment=SentimentOptions(targets=[dealerreview]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    
    return(label)
