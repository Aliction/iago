import json

class Slack_Card():
    def menu():
        menu_blocks = '[{"type":"actions","block_id":"HL+VY","elements":[{"type":"radio_buttons","action_id":"task_type","options":[{"text":{"type":"plain_text","text":"Update the Sheet","emoji":true},"value":"update_sheet"},{"text":{"type":"plain_text","text":"Create Drafts","emoji":true},"value":"create_drafts"},{"text":{"type":"plain_text","text":"Send Mails","emoji":true},"value":"send_emails"}]}]}]'
        return menu_blocks

    def access_card(auth_uri):
#        print(auth_uri)
        access_blocks = '[{"type": "section", "block_id": "KLGCq", "text": {"type": "mrkdwn", "text": "Access Required.", "verbatim": False}, "accessory": {"type": "button", "action_id": "grant_access", "text": {"type": "plain_text", "text": "Grant Access", "emoji": True}, "value": "click_me_123", "url": "' + auth_uri + '"}}]'
        return access_blocks

    def mail_confirmation(email_list):
        options = []
        for mail in email_list:
            option = {"text":{"type":"plain_text","text":mail,"emoji":True},"value":mail}
            options.append(option)
        options.append({"text":{"type":"plain_text","text":"another (provide it inthe chat)","emoji":True},"value":"Another"})
        mail_blocks_obj = [{"type":"section","text":{"type":"mrkdwn","text":"Can you select the mail to use for this operation or select another and provide it in the chat?"},"accessory":{"type":"radio_buttons","options":options,"action_id":"mail_selected"}}]

#        mail_blocks_obj = [{"type":"input","element":{"type":"radio_buttons","options":options,"action_id":"mail_selected"},"label":{"type":"plain_text","text":"Select an email","emoji":True}},{"type":"input","element":{"type":"plain_text_input","action_id":"new_mail"},"label":{"type":"plain_text","text":".. Or Enter a new e-mail","emoji":True}}]
        mail_blocks = json.dumps(mail_blocks_obj)
        print(mail_blocks)
        return mail_blocks

    def confirmation(confirmation_question, action_id, message_to_confirm):
        confirmation_obj = [{"type":"section","text":{"type":"mrkdwn","text": confirmation_question},"accessory":{"type":"radio_buttons","options":[{"text":{"type":"plain_text","text":"Yes","emoji":True},"value":message_to_confirm},{"text":{"type":"plain_text","text":"No","emoji":True},"value":"unconfirmed"}],"action_id": action_id}}]
        confirmation_block = json.dumps(confirmation_obj)
        return confirmation_block
