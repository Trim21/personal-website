import glob
import json
import pathlib
import sys
from os import path
from typing import List

project_dir = pathlib.Path(path.dirname(__file__)).parent
server_dir = project_dir / 'server'
data_dir = project_dir / 'bangumi-data'
sys.path.append(server_dir)

with open(server_dir / 'patch.json', 'r', encoding='utf8') as f:
    data = json.load(f)

file_list = glob.glob(str(data_dir / 'data' / 'items' / '*' / '*.json'))


def item_match_subject(d: dict, subject_id: str):
    return [
        x for x in d['sites']
        if x['site'] == 'bangumi' and x['id'] == subject_id
    ]


def match_item_by_subject(j: List[dict], subject_id):
    for item in j:
        if item_match_subject(item, subject_id):
            return item


def add_website(d: dict, website, bangumi_id):
    """
    True if has add website section to sites
    if not contains return false
    """
    b = [x for x in d['sites'] if x['site'] == website]
    if b:
        return False
    else:
        d['sites'].append({
            'site': website, 'id': bangumi_id, 'begin': d['begin'],
            'official': None, 'premuiumOnly': None, 'censored': None,
            'exist': True, 'comment': ''
        }, )
        return True


def get_subject_id(d: dict):
    b = [x for x in d['sites'] if x['site'] == 'bangumi']
    if b:
        return b[0]['id']


class MatchedSubjectFile():
    subject_to_file_map = {}
    for file in file_list:
        with open(file, 'r', encoding='utf8') as f:
            j = json.load(f)
            for item in j:
                s = get_subject_id(item)
                if s:
                    subject_to_file_map[s] = file

    def __init__(self, subject_id, mode):
        self.filename = None
        self.mode = mode
        if subject_id not in self.subject_to_file_map:
            raise FileNotFoundError(
                f'can\'t find file contains subject_id {subject_id}'
            )
        self.filename = self.subject_to_file_map[subject_id]

    def __enter__(self):
        self.open_file = open(self.filename, self.mode, encoding='utf8')
        return self.open_file

    def __exit__(self, *args):
        self.open_file.close()


def get_translate_or_raw_title(b: dict):
    return b.get('titleTranslate', {}).get('zh-Hans', [b['title']])[0]


if __name__ == '__main__':
    item_list = []
    for item in data:
        website = item['website']
        try:
            with MatchedSubjectFile(item['subject_id'], 'r') as f:
                j = json.load(f)
            b = match_item_by_subject(j, item['subject_id'])
            item['title'] = get_translate_or_raw_title(b)
            c = add_website(b, website, item['bangumi_id'])
            if c:
                with MatchedSubjectFile(item['subject_id'], 'w') as f:
                    f.write(
                        json.dumps(
                            j,
                            ensure_ascii=False,
                            indent=2,
                        ).replace('\r\n', '\n')
                    )
                    f.write('\n')
            else:
                item_list.append(item)
        except FileNotFoundError as e:
            item_list.append(item)
            print(e)
    #
    with open(server_dir / 'patch.json', 'w', encoding='utf8') as f:
        json.dump(item_list, f, ensure_ascii=False, indent=2)
