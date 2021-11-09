from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH
from flask import Flask, send_from_directory
from pywebio.input import *
from pywebio.output import *
import argparse
from pywebio import start_server

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np

gsheet_name = 'SUPER Project (All Data)'
json_credentials = 'super-project-324706-3389a6fde047.json'


def open_spreadsheet(sheet_name, json_credentials):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        json_credentials, scope)
    # authorize the clientsheet
    client = gspread.authorize(creds)
    # get the instance of the Spreadsheet
    return(client.open(sheet_name))

    # Returns sheet data in a pandas df


def get_sheet_data(spreadsheet, sheet_index):
    sheet = spreadsheet.get_worksheet(sheet_index)
    return(pd.DataFrame(sheet.get_all_values()[1:], columns=sheet.get_all_values()[0]))


def get_column_data(spreadsheet, sheet_index, column_name):
    sheet_data = spreadsheet.get_worksheet(sheet_index)
    sheet = pd.DataFrame(sheet.get_all_values()[
        1:], columns=sheet.get_all_values()[0])
    return(sheet[column_name])


def get_user_data():
    # Intro
    put_markdown(
        '# Stanford Behavior Design - Emotion Regulation Tool!')

    # Collecting User Data
    user_data = input_group("The following questions will help us match you with the best technique.", [
        # Step 1: Ask about the environment the person is in (e.g. Where are you and who is around)
        select("Which of the following best describes your current situation?", [
            'Waking up', 'At work', 'At home alone', 'At home with family or friends', 'About to go to bed'], name='environment', required=True),
        # Step 2: Ask about the current emotion the person is feeling (e.g. unmotivated, bored, sad, etc.)
        select("Which of the following best describes your emotional state?", [
            'Tired and unmotivated', 'Overwhelmed', 'Bored', 'Just "normal"', 'Sad', 'Stressed', 'Restless'], name='emotion', required=True)
    ])

    return(user_data["environment"], user_data["emotion"])


def get_random_technique(environment, emotion):
    spreadsheet = open_spreadsheet(gsheet_name, json_credentials)
    techniques = get_sheet_data(spreadsheet, 6)
    suggested_technique = techniques[techniques.Environment.eq(
        environment)][techniques.Emotion.eq(emotion)].Technique.values[0]
    return(suggested_technique)


def display_technique(environment, emotion, technique):
    put_markdown('## You are ' +
                 environment.lower() + " and are feeling " + emotion.lower() + '.')
    put_markdown(
        '### Here is a technique that other people use to upregualte positive emotions when they are in your situation:')
    put_markdown(technique)


def main():
    environment, emotion = get_user_data()
    technique = get_random_technique(environment, emotion)
    display_technique(environment, emotion, technique)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(main, port=args.port)
