from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as Soup
import time
import json
import csv
import random
from datetime import datetime

class WhoScoredScraper:
    def __init__(self, headless=False):
        self.BASE_URL = "https://www.whoscored.com"
        self.DIR = "/LiveScores"
        self.DAYS = 3
        self.LEAGUES = ['England-League-Two']
        self.HEADLESS = headless

        self.options = Options()
        if self.HEADLESS:
            self.options.add_argument("--headless")

        self.options.add_argument("--window-size=1920,1200")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

    def run_crawl(self):
        start = time.time()
        links = self.get_links(self.DAYS)
        quarter = time.time()
        print("Collecting All The links Took:", quarter - start, "Seconds")
        data = self.get_match_data(links)
        almost = time.time()
        print("Grabbing Matches Data Took:", almost - quarter, "Seconds")
        self.save_data(data)
        self.driver.close()
        self.driver.quit()
        end = time.time()
        print("Fully Scraper Took:", end - start, "Seconds")

    def get_match_data(self, data):
        # Loop through Matches Data
        for day, matches in data.items():
            for key, links in matches.items():
                for index, link in enumerate(links):
                    # Go To Match Details
                    self.driver.get(link)
                    # Wait For Page Refresh
                    time.sleep(random.randint(5, 10))
                    # Grab Page Source
                    page = Soup(self.driver.page_source, 'html.parser')

                    # Check if Match Has LiveStatistics Link And Go to That Link
                    if not page.select('a[href*="/LiveStatistics/"]'):
                        # Delete The Match Record Which does not have LiveStatistics
                        data[day][key].pop(index)
                        print(link, " <== was Deleted")
                        continue  # Skip the rest of the loop for this match

                    # Check if the page contains the expected elements
                    home_formation_elem = page.find('div',
                                                    attrs={'class': 'match-centre-header-team', 'data-field': 'home'})
                    if home_formation_elem is None:
                        continue  # Skip this match if the element is missing

                    # Now you can safely access elements if they exist
                    home_formation = home_formation_elem.find('div', attrs={'class': 'formation'}).text.strip()
                    away_formation = page.find('div',
                                               attrs={'class': 'match-centre-header-team', 'data-field': 'away'}).find(
                        'div', attrs={'class': 'formation'}).text.strip()
                    home_link = self.BASE_URL + page.find('div', attrs={'class': 'match-centre-header-team',
                                                                        'data-field': 'home'}).find('a', attrs={
                        'class': 'team-name'})['href']
                    away_link = self.BASE_URL + page.find('div', attrs={'class': 'match-centre-header-team',
                                                                        'data-field': 'away'}).find('a', attrs={
                        'class': 'team-name'})['href']
                    # Dive to Grab More Data in LiveStatistics
                    self.driver.get(link.replace('/Live/', '/LiveStatistics/'))
                    # Wait For Page Refresh
                    time.sleep(random.randint(5, 10))
                    # Grab Page Source
                    page = Soup(self.driver.page_source, 'html.parser')
                    # Collect Data
                    home_team = page.find('span', attrs={
                        'class': 'col12-lg-4 col12-m-4 col12-s-0 col12-xs-0 home team'}).text.strip()
                    score = page.find('span',
                                      attrs={'class': 'col12-lg-4 col12-m-4 col12-s-2 col12-xs-0 result'}).text.strip()
                    away_team = page.find('span', attrs={
                        'class': 'col12-lg-4 col12-m-4 col12-s-0 col12-xs-0 away team'}).text.strip()
                    match_name = ' '.join([home_team, score, away_team])
                    home_team_table = page.find('div', attrs={'id': 'live-player-home-stats'}).findAll('td', attrs={
                        'class': 'col12-lg-2 col12-m-3 col12-s-4 col12-xs-5 grid-abs overflow-text'})
                    away_team_table = page.find('div', attrs={'id': 'live-player-away-stats'}).findAll('td', attrs={
                        'class': 'col12-lg-2 col12-m-3 col12-s-4 col12-xs-5 grid-abs overflow-text'})
                    home_team_players = self.get_players(home_team_table)
                    away_team_players = self.get_players(away_team_table)
                    # Generate Final Data Source
                    data[day][key][index] = {
                        match_name: {
                            home_team: {
                                'Players': home_team_players,
                                'Formation': 'Formation: ' + home_formation,
                                'Team Link': home_link,
                            },
                            away_team: {
                                'Players': away_team_players,
                                'Formation': 'Formation: ' + away_formation,
                                'Team Link': away_link,
                            }
                        }
                    }
        # Return Data Result
        return data

    def get_links(self, days=1):
        # Define Url
        url = self.BASE_URL + self.DIR
        print(url)
        # Driver Get Main Url
        self.driver.get(url)
        # Wait For Page Load
        time.sleep(random.randint(5, 10))
        # Trying to Remove an Alert and Sleep for 4 Seconds
        self.remove_alert(True, random.randint(5, 10))
        # Define Links
        data = {}
        # Get Links
        for i in range(days):
            # Sleep at least 5 Seconds
            time.sleep(random.randint(5, 10))
            # Get The Day of Matches
            match_day = self.driver.find_element("xpath",
                                                 "//*[@id='toggleCalendar']//span[not(contains(@class, 'Calendar-module_arrow'))]").text.strip()
            if match_day == 'Today':
                now = datetime.now()
                # Convert the date to the desired format
                match_day = now.strftime("%a, %b %d %Y")
            # Put match_day as a Key of Links Data
            data[match_day] = self.get_valid_links(Soup(self.driver.page_source, 'html.parser'))

            if i < days:
                # Iterate to the previous day
                self.driver.find_element("xpath", "//button[@id='dayChangeBtn-prev']").click()
        # Return Data
        return data

    def get_valid_links(self, page):
        # Sleep at least 5 Seconds
        time.sleep(random.randint(5, 10))
        result = {}
        # Get All The Links
        links = list(map(lambda x: self.BASE_URL + x["href"], page.select('div[class *= "Match-module_scores"] a'))
                     # Check Leagues
                     for league in self.LEAGUES)
        for league in self.LEAGUES:
            filtered_links = [link for link in links if league in link]
            if filtered_links:
                result[league] = filtered_links
        return result

    def remove_alert(self, remove=False, sleep=0):
        if remove:
            try:
                self.driver.find_element("xpath", "//button[@mode='primary' and text()='AGREE']").click()
                time.sleep(sleep)
                return True
            except Exception:
                pass
        else:
            pass

    def get_players(self, table):
        team = []
        for row in table:
            player_name = row.a.span.text.strip()
            player_link = self.BASE_URL + row.a['href']
            if 'sub' in row.find_all('span')[2].text.lower():
                break
            else:
                team.append([player_name, player_link])
        return team

    def convert_dict_to_list(self, data):
        results = []
        for match_day in data:
            for league in data[match_day]:
                for key, game in enumerate(data[match_day][league]):
                    for team in data[match_day][league][key]:
                        try:
                            # len of data[match_day][league][key][team] always must be two
                            # First one is Home, Second One is Away
                            for player in data[match_day][league][key][team]:
                                details = data[match_day][league][key][team][player]
                                team_formation = details['Formation']
                                team_link = details['Team Link']
                                for p in data[match_day][league][key][team][player]["Players"]:
                                    # Append Data
                                    results.append([league, match_day, team, p[0], p[1], team_formation, team_link,
                                                    time.strftime("%x %r")])
                        except:
                            continue
        return results

    def save_json(self, data, json_file):
        with open(json_file, mode='w', encoding='utf-8') as j_file:
            json.dump(data, j_file)

    def save_data(self, data):
        with open('result.json', mode='a', encoding='utf-8') as j_file:
            json.dump(data, j_file)
        results = self.convert_dict_to_list(data)
        headers = ['League', 'Match Day', 'Match Name', 'Team', 'Player Name', 'Player Link', 'Team Formation',
                   'Team Link', 'Timestamp']
        # Saving result as csv
        with open('result.csv', mode='a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            writer.writerows(results)

# Main Loop
if __name__ == '__main__':
    scraper = WhoScoredScraper(headless=False)
    scraper.run_crawl()
