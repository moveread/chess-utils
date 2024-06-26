import re
from bs4 import BeautifulSoup, Tag
from haskellian import either as E, Left
from chess_pairings import GroupPairings
from .common import pairings_row, parse_row, extract_round, parse_columns

round_regex = re.compile(r'^Round \d+')

def round_rows(table: Tag) -> dict[str, list[Tag]]:
  rounds = {}
  current_round = None
  for row in table.find_all('tr'):
    if (match := round_regex.match(row.get_text())):
      current_round = match.group().strip().split(' ')[1]
      rounds[current_round] = []
    elif pairings_row(row):
      rounds[current_round].append(row)

  return rounds

@E.do()
def parse_single_round_robin(soup: BeautifulSoup) -> GroupPairings:
  columns = parse_columns(soup).unsafe()
  heading = soup.find(string=round_regex)
  if heading is None:
    Left('No round heading found').unsafe()
  table = heading.find_parent('table') # type: ignore
  if table is None:
    Left('No table found').unsafe()
  rounds = round_rows(table) # type: ignore

  output = {}
  for rnd, rows in rounds.items():
    pairs = extract_round(rows, columns).map(parse_row).sync()
    output[rnd] = {
      str(i+1): pair
      for i, pair in enumerate(pairs)
    }
  return output