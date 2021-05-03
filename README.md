# Iago - Email Messaging Automated System
Iago is a Google Chatbot that allows users to customize and send emails from inputted data from a Google Spreadsheet.

## Supportability
Currently, Iago is supported on: 
1. Google Chat 
2. Slack 

## Quickstart 
1. Create a Google Spreadsheet and label the active tab as "Iago" - this is required or the bot will not locate the inputted data. Here is a [template file](https://docs.google.com/spreadsheets/d/1MCf0II8vDfDoyAFzf-sdLgYkJj_P8AU9-GMAQC16zpg/edit?usp=sharing) that can be used as an example.

3. List customer info and other necessary input data (variables) as column headers. Then insert the necessary customer and event details under. 

4. There are two required columns: Subject, Message. This is where you want to draft your email subject and email subjects using the variables defined. 

    For example, you can draft your email subject saying "Have you registered for Red Hat Summit 2021 yet {First Name}?" and it calls the variables defined for your customer information (in this case, {First Name}).

5. Open Google Chat and open the message window for the Iago Bot. Input the URL link to the Google spreadsheet.

  Iago will ask if you want to:

    1. Only update sheet (outputs the email subject and message straight into sheets)
    2. Draft the email (create email drafts but won't send)
    3. Send mails (create email from input data and send the emails)


    NOTE: Iago will ask to Grant Iago Access to your Gmail account. Please sign in accordingly once the pop-up window appears.

5. Once you've selected the option, check respective output to verify the bot did what you asked.

    For example, I selected "Draft the email" and you can see the status update from Iago show:

    ```
    Authorization is successful
    Analyzing the sheet
    Processing the sheet ...
    The sheet has been updated
    I created the required draft e-mails
    ```

    In your corresponding Gmail account, check your Drafts folder to verify the emails were generated.


## To submit bugs/enhancements

If you run into any issues while using the tooling, you can submit a ticket to the author of the tool directly to GitHub:
[https://github.com/AlyIbrahim/iago/issues](https://github.com/AlyIbrahim/iago/issues)
