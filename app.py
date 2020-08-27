from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import requests
import json

app = Flask(__name__)
api = Api(app)

# Load values from config.py
app.config.from_object('config.Config')

headers = {"Authorization": "Bearer %s" % app.config['AUTH_TOKEN'] }

parser = reqparse.RequestParser()

class prometheus(Resource):
    # https://prometheus.io/docs/alerting/latest/configuration/#webhook_config
    # https://groups.google.com/g/prometheus-users/c/qg1BWbYAZ9o?pli=1
    
    def get(self):
        return "I'm here"
    
    def post(self):
        parser.add_argument('status', type=str)
        parser.add_argument('externalURL', type=str)
        parser.add_argument('alerts', type=str)
        parser.add_argument('status', type=str)
        parser.add_argument('commonLabels', type=dict)
        parser.add_argument('commonAnnotations', type=dict)
        args = parser.parse_args()

        if args.status == "firing":
            color = "red"
        elif args.status == "resolved":
            color = "green"
        else:
            color = "white"

        print(args)

        fields = []
        if isinstance(args.alerts, dict):
            alerts = args.alerts
        else:
            alerts = [eval(args.alerts)]

        for field in alerts:
            fields.append( {"title": "%s - %s" % (field['labels']['alertname'], field['labels']['instance']), "value": field['annotations']['description'], "short": "True" } )


        #print(args.commonAnnotations)
        payload = {
            "channel_id" : app.config['ALERTS_CHANNEL_ID'],
            "props": {"attachments": [{
                "pretext": args.commonAnnotations['description'],
                "text": args.commonLabels['alertname'],
                "color": color,
                "author_name": "Prometheus Alertmanager",
                "author_link": "https://prometheus.int.flattr.net/prometheus/alerts",
                "fields": fields,
                }]}
            }

        r = requests.post(app.config['ENDPOINT'], json=payload, headers=headers)
        print(r.text)

        return "Ok"

class grafana(Resource):
    def get(self):
        return "I'm here"
    
    def post(self):
        parser.add_argument('message', type=str)
        parser.add_argument('ruleName', type=str)
        parser.add_argument('ruleUrl', type=str)
        parser.add_argument('state', type=str)
        parser.add_argument('ruleName', type=str)
        parser.add_argument('title', type=str)
        parser.add_argument('evalMatches', type=str)
        args = parser.parse_args()

        if args.state == "alerting":
            color = "red"
        else:
            color = "blue"

        fields = []
        if isinstance(args.evalMatches, dict):
            evalMatches = args.evalMatches
        else:
            evalMatches = [eval(args.evalMatches)]

        for field in evalMatches:
            fields.append( {"title": field['metric'], "value": "%s" % field['value'], "short": "True" } )

        payload = {
            "channel_id" : app.config['ALERTS_CHANNEL_ID'],
            "props": {"attachments": [{
                "pretext": args.title, 
                "text": args.message,
                "color": color,
                "author_name": "Grafana",
                "author_link": "https://grafana.int.flattr.net",
                "author_icon": "http://lim1-webhooks-01.int.flattr.net/hotlink/grafana.png",
                "fields": fields,
                }]}
            }

        r = requests.post(app.config['ENDPOINT'], json=payload, headers=headers)
        print(r.text)

        return "Ok"

api.add_resource(grafana, '/grafana')
api.add_resource(prometheus, '/prometheus')