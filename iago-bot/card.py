class Card:
    def confirmation_card(question, action, confirmation_item, message_to_confirm):
        confirmation_card = {
    "cards": [{
        "header": {
            "title": "Iago",
            "subtitle": "Confirmation !",
            "imageUrl": "https://iago.aliction.com/avatar.png",
            "imageStyle": "IMAGE"
        },
        "sections": [{
            "widgets": [
              {
                "keyValue": {
                  "icon" : "EMAIL",
                  "topLabel": confirmation_item,
                  "content": message_to_confirm
                  }
              }
          ]
        },{
            "widgets": [{
                "buttons": [{
                    "textButton": {
                        "text": "Yes",
                        "onClick": {
                            "action": {
                                "actionMethodName": action,
                                "parameters":[
                                    {
                                        "key": confirmation_item,
                                        "value": message_to_confirm 
                                    },{
                                        "key": "confirmed",
                                        "value": True
                                    }

                                ]
                            }
                        }
                    }
                }, {
                    "textButton": {
                        "text": "No",
                        "onClick": {
                            "action": {
                                "actionMethodName": action,
                                "parameters":[
                                    {
                                        "key": confirmation_item,
                                        "value": message_to_confirm
                                    },{
                                        "key": "confirmed",
                                        "value": False 
                                    }
                                ]
                            }
                        }
                    }
                }]
            }]
        }]
    }]
}        
        return confirmation_card

    def access_card(self, auth_url):
        access_card = {
    "cards": [{
        "header": {
            "title": "Iago",
            "subtitle": "Access Required",
            "imageUrl": "https://iago.aliction.com/avatar.png",
            "imageStyle": "IMAGE"
        },
        "sections": [{
            "widgets": [{
                "buttons": [{
                    "textButton": {
                        "text": "Grant Iago Access",
                        "onClick": {
                            "openLink": {
                                "url": auth_url
                            }
                        }
                    }
                }]
            }]
        }]
    }]
}
        return access_card
        
    menu = {
    "cards": [{
        "header": {
            "title": "Iago",
            "subtitle": "Menu",
            "imageUrl": "https://iago.aliction.com/avatar.png",
            "imageStyle": "IMAGE"
        },
        "sections": [{
            "widgets": [{
                "buttons": [{
                    "textButton": {
                        "text": "Only Update Sheet",
                        "onClick": {
                            "action": {
                                "actionMethodName": "update_sheet",
                                "parameters":[
                                    {
                                        "key": "key_name",
                                        "value": "value"
                                    }
                                ]
                            }
                        }
                    }
                }]
            }]
        }, {
            "widgets": [{
                "buttons": [{
                    "textButton": {
                        "text": "Create Drafts",
                        "onClick": {
                            "action": {
                                "actionMethodName": "create_drafts"
                                }
                        }
                    }
                }]
            }]
        }, {
            "widgets": [{
                "buttons": [{
                    "textButton": {
                        "text": "Send Mails",
                        "onClick": {
                            "action": {
                                "actionMethodName": "send_emails"
                                }
                        }
                    }
                }]
            }]
        }]
    }]
}
