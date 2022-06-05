import collections
import os
import subprocess

from github import Github

from testing.utils import get_json_from_file, save_dict_to_json
from utils import DiscordWebhook, Logger
from utils.environment import env


class ContinuousIntegration:

    def __init__(self):
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.repo = Github(
            env.github_access_token).get_user().get_repo('olympus')
        if not os.path.exists('pull_requests.json'):
            save_dict_to_json({}, 'pull_requests.json')

        # TODO: Make a third text channel for PR bot

    def run_cycle(self):
        last_prs: dict = get_json_from_file('pull_requests.json')
        current_prs = self.repo.get_pulls()
        closed_prs = list(last_prs.keys())
        for current_pr in current_prs:
            newest_sha = None
            for commit in current_pr.get_commits():
                newest_sha = commit.sha

            current_number = str(current_pr.number)
            if current_number in closed_prs:
                closed_prs.pop(closed_prs.index(current_number))
            if current_number not in last_prs.keys():
                last_prs[current_number] = {
                    'title': current_pr.title,
                    'branch': current_pr.head.ref,
                    'number': current_number,
                    'state': current_pr.state,
                    'url': current_pr.html_url,
                    'newest_sha': newest_sha,
                    'tested_sha': None
                }
            else:
                last_prs[current_number]['title'] = current_pr.title
                last_prs[current_number]['branch'] = current_pr.head.ref
                last_prs[current_number]['state'] = current_pr.state
                last_prs[current_number]['state'] = current_pr.state
                last_prs[current_number]['newest_sha'] = newest_sha
        for closed_pr in closed_prs:
            last_prs.pop(closed_pr)
        save_dict_to_json(last_prs, 'pull_requests.json')

        sorted_prs = collections.OrderedDict(sorted(last_prs.items()))
        updated_prs = {}
        for pr in sorted_prs.values():
            newest_sha = pr.get('newest_sha')
            tested_sha = pr.get('tested_sha')
            # TODO: Shouldn't check for passing here. It'll cause crazy repeats
            if tested_sha is None or newest_sha != tested_sha:
                try:
                    # Its morbin time
                    branch = pr.get('branch')
                    filename = f"test-log-{branch}.txt"
                    process = subprocess.Popen(
                        f"cd ~/olympus && git checkout main && git pull && git fetch origin {branch} && git checkout {branch} && git pull origin {branch} && python unit_tests.py all {filename}",
                        shell=True
                    )
                    process.wait()

                    pr_info_str = f'''**Name:** {pr.get('title')}\n**Status:** {pr.get('state')}\n**Branch:** `{branch}`\n**URL:** <{pr.get('url')}>\n**SHA:** {newest_sha}'''
                    gh_pr = self.repo.get_pull(int(pr.get('number')))
                    if process.returncode == 0:
                        self.discord.send_alert(f"<a:DANKIES:927062701878947851> **==== PR Test Success ====** <a:DANKIES:927062701878947851>")
                        self.discord.send_alert(pr_info_str)
                        gh_pr.create_issue_comment(f'[AUTOMATED]* As of commit hash {pr.get("newest_sha")}, the PR has passed all unit tests.')
                    else:
                        if os.path.exists(filename):
                            with open(filename, 'r') as f:
                                test_log = f.read()
                            with open('debug-log.txt', 'r') as f:
                                debug_log = f.read()
                            test_results = "```" + test_log[test_log.index('=====================')+1:] + "```"
                            alert = f'''<:widepeepoSad1:662519773439197203><:widepeepoSad2:662519773514563614>  **=== PR Test Failed ===** <:widepeepoSad1:662519773439197203><:widepeepoSad2:662519773514563614>'''
                            self.discord.send_alert(alert)
                            self.discord.send_alert(pr_info_str)
                            self.discord.send_alert(test_results)
                        comment = f'[AUTOMATED] As of commit hash {pr.get("newest_sha")}, the PR has **FAILED** unit tests.\n\nMerging this branch may break production clusters! Check Discord for more infomoration.'
                        gh_pr.create_issue_comment(comment)
                    pr['tested_sha'] = newest_sha
                except Exception as e:
                    print(e)
                finally:
                    subprocess.Popen(
                        f"git checkout main && git pull", shell=True)
            updated_prs[int(pr.get('number'))] = pr
            try:
                os.remove('debug-log.txt')
                os.remove(filename)
            except:
                pass
        save_dict_to_json(updated_prs, 'pull_requests.json')
